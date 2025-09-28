# Claude Commands Guide

This guide documents the available Claude slash commands in SpaceWalker and how to create custom commands.

## Overview

Claude commands are markdown files in `.claude/commands/` that define reusable workflows and automation scripts. They help standardize common tasks and ensure consistent execution.

## Available Commands

### Core Workflow Commands

#### `/commit`
Commits changes following project standards with verification.
- Runs linting and tests before committing
- Follows conventional commit format
- Includes co-author attribution

#### `/complete-next-task`
Executes the next task from TaskMaster with full verification.
- Updates task status throughout execution
- Runs appropriate tests
- Documents verification results

#### `/init-context`
Loads project context at the start of a session.
- Reads CLAUDE.md instructions
- Loads relevant documentation
- Sets up for current branch/task

### PR and Review Commands

#### `/review-pr-comments`
Analyzes PR comments and provides numbered action items for easy selection.
- Uses pr-review-analyzer agent with `just gh-pr comments`
- Presents actionable feedback as numbered items
- Supports flexible selection (e.g., "1,3" or "all")

```bash
# Review current branch's PR
/review-pr-comments

# Review specific PR
/review-pr-comments 290
```

#### `/request-review`
Updates PR description and requests review.
- Summarizes changes made
- Updates PR body
- Can request specific reviewers

#### `/generate-pr-title-description`
Creates PR title and description from changes.
- Analyzes git diff
- Follows PR template
- Links to Linear tickets

### Development Commands

#### `/fix-linear-issue <issue-id>`
Complete workflow for fixing a Linear issue.
- Creates branch
- Updates task status
- Implements fix with verification

#### `/create-tasks-from-linear`
Imports Linear issues into TaskMaster.
- Fetches assigned issues
- Creates local tasks
- Sets priorities

#### `/update-linear-ticket`
Syncs PR progress back to Linear.
- Updates issue status
- Adds PR link
- Posts progress comments

### Release Management

#### `/changelog-add`
Adds entry to changelog following keep-a-changelog format.
- Categorizes changes correctly
- Maintains format consistency
- Prepares for release

#### `/changelog-release`
Prepares changelog for release.
- Moves unreleased to version section
- Updates version numbers
- Creates release commit

#### `/version-bump`
Updates version numbers across the project.
- Updates package.json files
- Updates version constants
- Maintains consistency

#### `/smart-dev-to-main`
Orchestrates dev→main merge workflow.
- Ensures CI passing
- Creates merge PR
- Handles deployment

### Utility Commands

#### `/create-command`
Creates a new Claude command from template.
- Interactive command builder
- Follows command patterns
- Adds to commands directory

#### `/cleanup-docs-justfile`
Reviews and updates documentation after development.
- Identifies outdated docs
- Suggests justfile commands
- Updates INDEX.md

#### `/analyze-ci-failure`
Investigates CI/CD failures with detailed analysis.
- Fetches failure logs
- Identifies root causes
- Suggests fixes

### TaskMaster Commands (`/tm/*`)

The TaskMaster suite provides comprehensive task management:

```bash
/tm/help              # Show all TM commands
/tm/next              # Get next priority task
/tm/add              # Add new task
/tm/board            # Visual task board
/tm/workflows/daily  # Daily standup workflow
```

See `@.claude/TM_COMMANDS_GUIDE.md` for complete TaskMaster documentation.

## Command Structure

Each command file follows this structure:

```markdown
# Command Name

Brief description of what the command does.

## Usage
```
/command-name [required-arg] [optional-arg]
```

## Purpose
Detailed explanation of when and why to use this command.

## Implementation
Step-by-step workflow the command follows:

1. **Phase 1**: Description
   - Specific actions
   - Tools used

2. **Phase 2**: Description
   - More actions
   - Verification steps

## Examples
Concrete usage examples with expected outcomes.

## Safety Considerations
Any warnings or safety checks.

## Related Commands
Links to similar or complementary commands.
```

## Creating Custom Commands

### 1. Create Command File

```bash
# Use the create-command helper
/create-command

# Or manually create
touch .claude/commands/my-command.md
```

### 2. Define Command Structure

```markdown
# My Command

What this command does.

## Usage
```
/my-command <required> [optional]
```

## Implementation

### Phase 1: Setup
1. Validate inputs
2. Check prerequisites
3. Load necessary context

### Phase 2: Execution
1. Main logic here
2. Use appropriate tools
3. Verify results

### Phase 3: Cleanup
1. Update documentation
2. Commit changes
3. Report results
```

### 3. Command Best Practices

1. **Single Responsibility** - Each command does one thing well
2. **Verification Focus** - Always include verification steps
3. **Safety First** - Check before destructive operations
4. **Clear Documentation** - Examples and use cases
5. **Tool Integration** - Prefer justfile commands over raw tools

### 4. Testing Commands

Before adding to the repository:
1. Test with various inputs
2. Verify safety checks work
3. Ensure idempotency where possible
4. Document edge cases

## Command Patterns

### Workflow Commands
Commands that orchestrate multi-step processes:
- Start with context gathering
- Execute in clear phases
- Include verification between phases
- End with cleanup/documentation

### Analysis Commands
Commands that provide insights:
- Fetch data from multiple sources
- Process and correlate information
- Present actionable findings
- Suggest next steps

### Automation Commands
Commands that automate repetitive tasks:
- Replace manual command sequences
- Include error handling
- Provide progress feedback
- Support dry-run mode

## Integration with Project Workflows

Commands integrate with:
- **TaskMaster** - Task tracking and status updates
- **Justfile** - Standardized command execution
- **Git/GT** - Version control operations
- **Linear** - Issue tracking synchronization
- **CI/CD** - Build and deployment automation

## Troubleshooting

### Command Not Found
```bash
# List all commands
ls -la .claude/commands/

# Check command name spelling
ls .claude/commands/ | grep -i commandname
```

### Command Fails
1. Check prerequisites (API keys, tools installed)
2. Verify current directory is project root
3. Review command implementation for issues
4. Check related tool availability

### Creating Command Issues
- Ensure markdown formatting is valid
- Check file permissions
- Verify command doesn't conflict with existing ones

## Future Enhancements

Potential improvements for the command system:
- Command aliases for common variations
- Parameter validation framework
- Command composition/chaining
- Performance metrics tracking
- Command version management

## Related Documentation

- [TaskMaster Guide](@.claude/TM_COMMANDS_GUIDE.md) - Complete task management
- [Justfile Workflow](../claude-components/justfile-workflow.md) - Using just commands
- [Development Setup](../setup/development-setup.md) - Environment configuration
