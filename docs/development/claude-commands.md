---
purpose: "Catalog shared Claude slash commands and describe when to apply them."
audience: "Developers, reviewers, automation engineers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# Claude Commands Guide

This guide documents the available Claude slash commands in SpaceWalker and how
to create custom commands.

## Overview

Claude commands are markdown files in `.claude/commands/` that define reusable
workflows and automation scripts. They help standardize common tasks and ensure
consistent execution.

## When to Use This

- Invoke standardized automation in Claude chats without recalling justfile
  syntax.
- Review command behavior before editing or adding new slash commands.

## Prerequisites

- Repository clone with `.claude/commands/` available.
- Access to Claude with slash command support.

## Available Commands

### Documentation Analysis Commands

#### `/ground-truth`

Verifies what documentation claims versus what source code actually implements.

- Analyzes actual source code implementations using ast-grep
- Examines configuration and test files
- Identifies gaps between documented and actual behavior
- Provides structured gap analysis report

```bash
# Verify authentication implementation
/ground-truth "CSRF authentication"

# Check API implementation details
/ground-truth "JWT token handling"

# Analyze workflow implementation
/ground-truth "user registration flow"
```

## Command Structure

Each command file follows this structure:

````markdown
# Command Name

Brief description of what the command does.

## Usage

```bash
/command-name [required-arg] [optional-arg]
```
````

## Purpose

Detailed explanation of when and why to use this command.

## Implementation Template

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

## Creating Custom Commands

### 1. Create Command File

```bash
# Manually create command file
touch .claude/commands/my-command.md
```

### 2. Define Command Structure

```markdown
# My Command

What this command does.

## Usage

    /my-command {required} [optional]
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

- **Justfile** - Standardized command execution
- **Git/GT** - Version control operations
- **CI/CD** - Build and deployment automation

## Verification

- Run `/ground-truth --help` in Claude and confirm the description matches
  this guide.
- Ensure new or updated commands include runnable examples before merging
  related changes.

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

- Justfile Workflow – Reference the core project justfile patterns for
  command usage.
- Development Setup – Follow the repository README/CLAUDE instructions for
  local environment configuration.
