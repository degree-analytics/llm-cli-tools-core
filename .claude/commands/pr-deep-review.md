# PR Deep Review

Performs deep AI-powered validation of PR review comments by launching parallel sub-agents to investigate each issue.

## Usage
```
/pr-deep-review <pr_number>
```

## Purpose
Takes PR review comments and launches parallel expert agents to:
- Deep dive into relevant files for each issue
- Validate if the reviewer's concern is correct
- Recommend whether to address it and why
- Return findings for user decision

## What This Command Does

### Phase 1: Collect PR Issues
1. **Get PR Review Comments**:
```bash
# Get all review comments from the PR
gh api repos/{owner}/{repo}/pulls/<pr_number>/comments --jq '.[] | {
  id: .id,
  path: .path,
  line: .line,
  body: .body,
  user: .user.login,
  created_at: .created_at
}'

# Get PR review comments (top-level reviews)
gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews --jq '.[] | {
  id: .id,
  body: .body,
  user: .user.login,
  state: .state
}'

# Get issue comments on the PR
gh api repos/{owner}/{repo}/issues/<pr_number>/comments --jq '.[] | {
  id: .id,
  body: .body,
  user: .user.login,
  created_at: .created_at
}'
```

2. **Parse Issues**: Extract all actionable review comments (exclude resolved/dismissed)

3. **Confirm Scope**: Show count and ask "Launching N parallel agents to investigate these issues. Continue?"

### Phase 2: Parallel Deep Investigation
4. **Launch Sub-Agents**: For each issue, create Task agent with:
   - **Context**: Full list of ALL issues in PR for awareness
   - **Focus**: Single specific issue to investigate
   - **Mission**:
     - Read relevant files mentioned in issue
     - Understand the code context
     - Validate if reviewer's concern is correct
     - Assess severity and impact
     - Recommend: ADDRESS (with reason) or SKIP (with reason)
   - **Return**: Structured recommendation

5. **Execute in Parallel**: Launch all Task agents simultaneously (single message, multiple tool calls)

### Phase 3: Collect and Synthesize
6. **Gather Results**: Collect all agent recommendations

7. **Present Summary**: Format as numbered action list:
   ```
   PR #[number]: Deep Review Analysis
   Analyzed X issues with parallel expert agents

   🟢 RECOMMENDED TO ADDRESS (X items)
   [1] Original Issue - file.ext:line
       Reviewer: @name: "quote"
       Agent Finding: [validation of issue]
       Recommendation: Address because [specific reasoning]
       Estimated Effort: ~X min

   🟡 UNCERTAIN / NEEDS DISCUSSION (X items)
   [N] Original Issue - file.ext:line
       Agent Finding: [concerns or uncertainties]
       Recommendation: Discuss with team because [reasoning]

   🔴 RECOMMENDED TO SKIP (X items)
   [N] Original Issue - file.ext:line
       Agent Finding: [why issue is not valid/relevant]
       Recommendation: Skip because [specific reasoning]

   → Which should I fix? Reply with numbers (e.g. "1,4", "all recommended", or "none"):
   ```

### Phase 4: USER SELECTION HANDLING (ONLY after user responds)
8. **STOP AND WAIT** for user selection
9. **ONLY AFTER user responds**:
   - Parse selection (e.g., "1,4", "all recommended", "none")
   - Create TodoWrite tasks for selected items
   - Begin implementation with task tracking

## Sub-Agent Prompt Template

```markdown
# PR Issue Deep Investigation

## Context: All PR Issues
[Provide summary of ALL issues in the PR]

## Your Focus: Issue #[N]
**Original Comment**: @reviewer: "[exact quote]"
**File**: [file path]:[line]
**Category**: [issue type]

## Your Mission
1. **Read Files**: Examine the files mentioned in this issue
2. **Understand Context**: Look at surrounding code, related functions, imports
3. **Validate Concern**: Is the reviewer's concern technically correct?
4. **Assess Impact**: If correct, how severe is the issue?
5. **Recommendation**: Should we address this? Why or why not?

## Required Output Format
```json
{
  "issue_number": N,
  "is_valid": true/false,
  "severity_assessment": "critical|high|medium|low|not-applicable",
  "recommendation": "address|discuss|skip",
  "reasoning": "Detailed explanation of your findings and recommendation",
  "effort_estimate_minutes": X,
  "additional_concerns": "Any related issues you discovered"
}
```

## Investigation Rules
- **Be Critical**: Don't assume reviewer is always right
- **Be Thorough**: Check related code, tests, dependencies
- **Be Specific**: Reference line numbers and exact code in your reasoning
- **Be Honest**: If uncertain, recommend "discuss" not "address" or "skip"
- **Consider Context**: Is this consistent with existing codebase patterns?
```

## Selection Options
- `1,4` - Fix specific items by number
- `all` - Fix everything recommended
- `all recommended` - Fix only items agents recommend addressing
- `all uncertain` - Fix items needing discussion
- `none` or `skip` - Don't fix anything

## Implementation Notes

### Parallel Agent Execution
```python
# Launch all agents in single message with multiple Task tool calls
# DO NOT launch sequentially - must be parallel for performance
```

### Agent Type
- Use `subagent_type: "general-purpose"` for file analysis and code investigation

### Error Handling
- If any agent fails, continue with others and note the failure
- Present partial results if some agents succeed

### Performance Considerations
- Agents run in parallel (should complete in ~1-2 minutes total)
- Each agent has access to file reading tools
- Agents can use Grep/Glob for code discovery

## Fetching GitHub Data

### Get Repository Info
```bash
# Current repo owner and name
gh repo view --json owner,name --jq '{owner: .owner.login, name: .name}'
```

### Parse Review Comments
Look for:
- Bot comments (github-actions, claude, codex)
- Human reviewer comments
- Inline file comments with line numbers
- Top-level review summaries

Filter out:
- Resolved comments
- Outdated comments on changed lines
- Auto-generated stack comments (Graphite)

## Example Interaction

```
User: /pr-deep-review 5

Claude: Fetching review comments from PR #5...
        Found 6 actionable issues
        Launching 6 parallel expert agents to investigate...
        [waits for agents to complete]

        PR #5: Deep Review Analysis
        Analyzed 6 issues with parallel expert agents

        🟢 RECOMMENDED TO ADDRESS (3 items)
        [1] Missing permissions block - .github/workflows/notify-slack.yml:10
            Reviewer: @github-advanced-security: "Workflow does not contain permissions"
            Agent Finding: Confirmed - workflow lacks explicit permissions, security best practice
            Recommendation: Address - add permissions block for security compliance
            Estimated Effort: ~2 min

        [2] Incorrect condition - .github/workflows/notify-slack.yml:12
            Reviewer: @codex: "event check prevents workflow from running"
            Agent Finding: Confirmed - checks event == 'workflow_run' but should check conclusion
            Recommendation: Address - critical bug that blocks feature from working
            Estimated Effort: ~1 min

        🟡 UNCERTAIN / NEEDS DISCUSSION (1 item)
        [3] Untrusted code checkout - .github/workflows/slack-message.yml:95
            Agent Finding: Security concern valid but low risk for internal repo
            Recommendation: Discuss - assess risk vs effort tradeoff

        🔴 RECOMMENDED TO SKIP (2 items)
        [4] Overengineering concern
            Agent Finding: Current implementation is clear and maintainable
            Recommendation: Skip - no evidence of actual complexity issues

        → Which should I fix? Reply with numbers:

User: 1,2

Claude: Creating tasks for items 1 and 2...
        [uses TodoWrite to create tasks]
        [begins implementation]
```

## Related Commands
- `/pr-analyze-comments` - Quick analysis without deep investigation
- `/commit` - Commit fixes after implementation

## When to Use This vs pr-analyze-comments
- **pr-analyze-comments**: Fast, trust reviewers, implement suggestions directly
- **pr-deep-review**: Validate feedback first, especially for:
  - Large PRs with many comments
  - Conflicting reviewer opinions
  - Comments that might be outdated
  - When you're unsure if suggestions are correct

## Notes
- Uses GitHub CLI (`gh api`) for fetching review data
- Launches parallel Task agents for investigation
- Provides structured recommendations with reasoning
- User maintains final decision control
