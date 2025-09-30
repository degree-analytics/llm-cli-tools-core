# Request Code Review Command

Generate comprehensive PR review requests with detailed analysis for consistent, high-quality GitHub comments that guide reviewers effectively.

## Usage
```
/pr-request-review <PR_NUMBER>
```

## Purpose
Automatically analyze a PR and post a structured review request comment that helps reviewers understand:
- What changed and why
- Where to focus their attention
- Key areas of concern or complexity
- Context needed for effective review

## Implementation

### Phase 1: Validate and Collect PR Data
```bash
# 1. Validate PR exists and get basic info
gh pr view <pr_number> --json number,title,state,author,headRefName,baseRefName,url

# 2. Get PR commits for change analysis
gh pr view <pr_number> --json commits --jq '.commits[] | {message: .messageHeadline, sha: .oid, author: .author.login}'

# 3. Get PR diff for file changes
gh pr diff <pr_number>

# 4. Get changed files summary
gh pr view <pr_number> --json files --jq '.files[] | {path: .path, additions: .additions, deletions: .deletions}'
```

### Phase 2: Analyze Changes
Analyze the collected data:
- Identify modified files and their impact
- Categorize changes (features, fixes, refactors, tests, docs)
- Assess complexity and risk level
- Identify areas needing careful review

### Phase 3: Generate Review Request Comment

Create a structured comment in `.build/tmp/pr-review-request-<number>.md`:

**CRITICAL**: Comment MUST start with reviewer tags to trigger automation!

```markdown
@claude @codex — please review

## Review Request

**PR Summary**: [1-2 sentence overview of what this PR does]

### Changes Made
[Summary of key changes from commits and diff analysis]
- **[Category]**: [Specific changes and files]
  - [Details of what changed]
- **[Category]**: [Specific changes and files]
  - [Details of what changed]

### Review Focus Areas
Please pay special attention to:

1. **[Category]** - [specific files or areas]
   - [Why this area needs careful review]
   - [Specific concerns or questions]

2. **[Category]** - [specific files or areas]
   - [Why this area needs careful review]

### Test Coverage
- [X] Unit tests added/updated
- [X] Integration tests considered
- [ ] Manual testing performed

### Risk Assessment
**Risk Level**: [Low/Medium/High]
- [Key risks or concerns identified]
- [Mitigations in place]

### Context
[Any additional context reviewers should know]
- Related PRs or issues
- Design decisions made
- Known limitations or follow-ups

---
Ready for review
```

### Phase 4: Post Comment
```bash
# Ensure directory exists
mkdir -p .build/tmp

# Post the comment to GitHub
gh pr comment <pr_number> --body-file .build/tmp/pr-review-request-<number>.md

# Verify posting succeeded
echo "Comment posted successfully to PR #<pr_number>"
```

## Review Focus Categories

Common areas to highlight:
- **Logic/Algorithm Changes** - Core business logic modifications
- **API Changes** - Public interfaces or breaking changes
- **Security** - Authentication, data validation, secrets handling
- **Performance** - Potential bottlenecks or optimizations
- **Configuration** - Settings, environment variables, dependencies
- **Error Handling** - Edge cases and failure modes
- **Testing** - Test coverage and quality
- **Documentation** - README, docstrings, comments

## Smart Analysis Guidelines

### Identify Key Changes
From commits and diff:
- What files changed most significantly?
- What functionality was added/modified?
- Were there any refactorings or structural changes?
- Are there new dependencies or configuration changes?

### Assess Complexity
- **Low**: Documentation, minor fixes, simple additions
- **Medium**: New features, moderate refactors, API changes
- **High**: Complex algorithms, breaking changes, architectural shifts

### Determine Risk Areas
- Changes to critical paths (config, storage, providers)
- Large refactorings that affect many files
- New external dependencies or integrations
- Changes without adequate test coverage

## Example Workflows

### Standard Review Request
```bash
# Analyze PR #5
gh pr view 5 --json number,title,commits,files
gh pr diff 5

# Generate analysis and create comment file
# [analyze changes and create structured comment]

# Post comment
mkdir -p .build/tmp
gh pr comment 5 --body-file .build/tmp/pr-review-request-5.md
```

### Complex PR Analysis
For PRs with >10 files or complex changes:
1. Identify highest-risk changes first
2. Group related changes together
3. Generate more detailed review focus sections
4. Include specific line references in comments

## Error Handling

### PR Not Found
```
Error: PR #<number> not found
Please verify the PR number and try again.
```

### GitHub Authentication
If `gh` commands fail:
```
Error: GitHub authentication required
Run: gh auth login
```

### File Write Failures
If `.build/tmp/` directory issues:
```bash
mkdir -p .build/tmp
chmod 755 .build/tmp
```

## Safety Considerations

- **File Location**: Always uses `.build/tmp/` (project standard)
- **Read-Only Analysis**: No modifications to PR or repository code
- **GitHub CLI**: Uses official `gh` tool for all GitHub operations
- **Markdown Safety**: Properly escapes code blocks and special characters

## Integration with Repository Workflow

- **Structured Output**: Consistent comment format for all PRs
- **Reviewer-Focused**: Provides actionable guidance, not just description
- **Bot Integration**: Tags @claude and @codex to trigger automated reviews

## Related Commands
- `/pr-analyze-comments` - Review feedback after comments arrive
- `/pr-deep-review` - Deep validation of review comments
- `/commit` - Create commits before requesting review

## Notes
- Uses GitHub CLI (`gh`) for all GitHub operations
- Generates structured, reviewer-friendly comments
- Safe file handling in `.build/tmp/` directory
- Can be customized per project's review culture

## Expected Output

After running `/pr-request-review 5`:

```
Analyzing PR #5...
- Collected PR metadata ✓
- Analyzed commits and changes ✓
- Reviewed file changes (2 files modified) ✓
- Generated review request ✓

Posted review request comment to PR #5 ✓

View PR: https://github.com/degree-analytics/llm-cli-tools-core/pull/5
```
