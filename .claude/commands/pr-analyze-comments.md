# Analyze PR Comments

Analyzes PR review comments and presents numbered action items that you can easily select to fix.

## Usage
```
/pr-analyze-comments <pr_number>
```

## Purpose
Gets PR review comments and presents them as numbered action items so you can say "fix 1,5,9" etc.

Notes:
- Reviews may include comments from multiple bots (Claude and Codex). Treat both as authoritative inputs for parsing/resolution.

## What This Command Does

1. Requires a PR number to be provided
2. Fetches PR review data using GitHub CLI
3. Analyzes what needs to be done with AI assistance
4. Presents as numbered list with priority markers

**Note**: If no PR number is provided, the command will ask for one.

## Implementation

### Phase 1: Validate and Fetch PR Data
1. **Validate PR Number**: Ensure PR number is provided

2. **Get PR Basic Info**:
```bash
gh pr view <pr_number> --json number,title,state,url
```

3. **Fetch All Review Comments**:
```bash
# Get inline review comments on code
gh api repos/{owner}/{repo}/pulls/<pr_number>/comments --jq '.[] | {
  id: .id,
  path: .path,
  line: .line,
  body: .body,
  user: .user.login,
  created_at: .created_at,
  in_reply_to_id: .in_reply_to_id
}'

# Get top-level review comments
gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews --jq '.[] | select(.state != "DISMISSED") | {
  id: .id,
  body: .body,
  user: .user.login,
  state: .state,
  submitted_at: .submitted_at
}'

# Get general issue comments
gh api repos/{owner}/{repo}/issues/<pr_number>/comments --jq '.[] | {
  id: .id,
  body: .body,
  user: .user.login,
  created_at: .created_at
}'
```

4. **Get Repository Context**:
```bash
gh repo view --json owner,name --jq '{owner: .owner.login, name: .name}'
```

### Phase 2: Analyze and Categorize Comments
5. **Parse Comments**: Extract actionable feedback from:
   - Bot review comments (@github-actions, @claude, @codex, @github-advanced-security)
   - Human reviewer comments
   - Filter out:
     - Resolved/outdated comments
     - Auto-generated stack comments (Graphite, etc.)
     - Success/acknowledgment messages

6. **Categorize by Priority**:
   - **🔴 CRITICAL/BLOCKING**: Security issues, bugs that break functionality, test failures
   - **🟡 IMPORTANT**: Missing features, significant improvements, maintainability issues
   - **🔵 NICE TO HAVE**: Code style, minor optimizations, suggestions

7. **Structure Each Item**:
   ```
   [N] Issue Type - file.ext:line
       @reviewer: "exact quote from comment"
       Context: explanation why this matters
       Fix: specific implementation steps
       Effort: ~X min | Files: path/to/files
   ```

### Phase 3: DISPLAY AND STOP
8. Present the analysis in this format:
   ```
   PR #[number]: [title]
   Status: X outstanding issues

   🔴 CRITICAL/BLOCKING (X items) - Must fix before merge
   [1] Issue Type - file.ext:line
       @reviewer: "exact quote from comment"
       Context: explanation why this matters
       Fix: specific implementation steps
       Effort: ~X min | Files: path/to/files

   🟡 IMPORTANT (X items) - Should fix
   [N] Issue Type - file.ext:line
       @reviewer: "exact quote"
       Context: explanation
       Fix: implementation steps
       Effort: ~X min | Files: paths

   🔵 NICE TO HAVE (X items) - Optional improvements
   [N] Issue Type - file.ext:line
       @reviewer: "exact quote"
       Fix: implementation steps
       Effort: ~X min | Files: paths

   Total estimated effort: ~X minutes/hours
   → Which should I fix? Reply with numbers (e.g. "1,4", "all critical", or "all"):
   ```

9. **⚠️ CRITICAL: STOP HERE - DO NOT PROCEED**
   - **WAIT for user to respond with their selection**
   - **DO NOT automatically select items or start fixing**

### Phase 4: USER SELECTION HANDLING (ONLY after user responds)
10. **ONLY AFTER user provides selection** (e.g. "1,4", "all critical"):
    - Parse their selection
    - Create TodoWrite tasks for selected items
    - Then proceed to implement the selected fixes
    - If user says "none" or "skip", acknowledge and stop

## Priority Assignment Guidelines

### 🔴 CRITICAL/BLOCKING
- Security vulnerabilities (XSS, SQL injection, exposed secrets)
- Bugs that prevent core functionality from working
- Test failures or missing critical test coverage
- Breaking changes without proper handling
- CI/CD pipeline failures

### 🟡 IMPORTANT
- Missing error handling for important flows
- Performance issues in key paths
- Missing documentation for public APIs
- Code duplication or maintainability concerns
- Missing permissions or access controls

### 🔵 NICE TO HAVE
- Code style suggestions
- Minor optimizations
- Improved naming
- Additional edge case handling
- Refactoring suggestions

## Example Usage

```bash
# Review specific PR
/pr-analyze-comments 5

# If no PR number provided, you'll be asked:
/pr-analyze-comments
→ "Please provide a PR number to review (e.g., /pr-analyze-comments 5)"
```

## Expected Interaction Flow

```
User: /pr-analyze-comments 5
Claude: Fetching PR review comments...
        Analyzing 8 comments from @claude, @codex, and @github-advanced-security...

        PR #5: feat: add Slack notifications for releases
        Status: 6 outstanding issues

        🔴 CRITICAL/BLOCKING (2 items) - Must fix before merge
        [1] Workflow Condition Bug - .github/workflows/notify-slack.yml:12
            @codex: "event check prevents workflow from running"
            Context: Workflow will never trigger - blocks entire feature
            Fix: Change condition from event == 'workflow_run' to conclusion == 'success'
            Effort: ~1 min | Files: .github/workflows/notify-slack.yml

        [2] Missing Permissions - .github/workflows/slack-message.yml:42
            @github-advanced-security: "Workflow does not contain permissions"
            Context: Security best practice violation
            Fix: Add permissions block with contents: read
            Effort: ~2 min | Files: .github/workflows/slack-message.yml

        🟡 IMPORTANT (2 items) - Should fix
        [3] Untrusted Code Checkout - .github/workflows/slack-message.yml:95
            @github-advanced-security: "Potential execution of untrusted code"
            Fix: Add validation or limit checkout scope
            Effort: ~10 min | Files: .github/workflows/slack-message.yml

        🔵 NICE TO HAVE (2 items) - Optional improvements
        [4] Simplify Implementation
            @claude: "272 lines for Slack message - consider marketplace action"
            Fix: Research and potentially adopt existing action
            Effort: ~30 min | Files: .github/workflows/slack-message.yml

        Total estimated effort: ~43 minutes
        → Which should I fix? Reply with numbers (e.g. "1,4", "all critical", or "all"):

Claude: [STOPS AND WAITS HERE]

User: fix 1,2

Claude: Creating tasks for items 1 and 2...
        [uses TodoWrite to create tasks]
        [begins implementation]

OR

User: none

Claude: Understood, no fixes will be applied.
```

## Selection Options
- `1,4` - Fix specific items by number
- `all` - Fix everything
- `all critical` - Fix all critical/blocking items
- `all important` - Fix all important items
- `1-3` - Fix range of items 1 through 3
- `none` or `skip` - Don't fix anything

## Error Handling

### PR Not Found
```
Error: PR #<number> not found
Please verify the PR number and try again.
```

### No Comments Found
```
No review comments found for PR #<number>
The PR may not have been reviewed yet.
```

### GitHub Authentication
If `gh` commands fail:
```
Error: GitHub authentication required
Run: gh auth login
```

## Notes

- Uses GitHub CLI (`gh api`) for fetching review data
- Analyzes comments from bots (@claude, @codex) and human reviewers
- Automatically categorizes by priority based on content
- User maintains control over what gets fixed
- Integration with TodoWrite for task tracking

## Related Commands
- `/pr-deep-review` - Deep agent investigation before implementing
- `/commit` - Commit fixes after implementation
- `/pr-request-review` - Request new review after fixes
