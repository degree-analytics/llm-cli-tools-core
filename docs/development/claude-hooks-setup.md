---
purpose:
  "Explain how to enable and validate Claude Code project hooks for
  llm-cli-tools-core-derived repositories."
audience:
  "Developers and automation engineers using Claude Code with llm-cli-tools-core"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# 🪝 Claude Code Hooks Setup Guide

**llm-cli-tools-core includes project-specific Claude Code hooks for enhanced
development workflow.**

## Overview

Our hooks provide:

- **Lint-on-Save**: Instant feedback when editing code files
- **Search Year Update**: Automatically updates outdated years in web searches

## When to Use This

- Local Claude Code sessions need the repository-specific automation.
- Hooks stop triggering and you need to verify expected files.

## Prerequisites

- Clone of the repository with `.claude/hooks/` checked in.
- Claude Code or Claude Desktop with project hook execution enabled.

## Quick Setup

### 1. Verify Hook Files Exist

```bash
ls .claude/hooks/
# Should show:
# lint-on-save.sh
# update-search-year.sh

ls .claude/settings.json
# Should exist
```

### 2. Enable Project Hooks in Claude Code

Claude Code automatically detects and uses project-specific settings when
working in this repository. **No additional setup required!**

The hooks are enabled by default when you work in the llm-cli-tools-core directory.

## How It Works

### Lint-on-Save Hook

- **Trigger**: When you edit/write Python (.py) or TypeScript
  (.ts/.tsx/.js/.jsx) files
- **Action**: Runs `just lint check`
- **Output**: Shows warnings for lint issues (never blocks saves)
- **Performance**: <500ms execution (0.5s timeout in settings), only checks the
  single edited file

**Example**:

```text
⚠️  main.py:
src/llm_cli_core/main.py:15:1: F401 'os' imported but unused
```

### Search Year Update Hook

- **Trigger**: When you use WebSearch tool
- **Action**: Updates outdated years (2024 and older) to current/range
- **Logic**:
  - Documentation queries: `2022` → `2024-2025`
  - General queries: `2023` → `2025`
  - Ignores version numbers and current year (2025)
- **Performance**: <100ms execution (0.1s timeout in settings)

**Example**:

```text
Query: "fastapi docs 2024"
Updated: "fastapi docs 2024-2025"
📅 Updated: 2024 → 2024-2025
```

## Hook Configuration

### Project Settings (`.claude/settings.json`)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/update-search-year.sh",
            "timeout": 0.1 // 100ms (timeout is in seconds)
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/lint-on-save.sh",
            "timeout": 0.5 // 500ms (timeout is in seconds)
          }
        ]
      }
    ]
  }
}
```

### Hook Scripts

#### Lint-on-Save (`lint-on-save.sh`)

- Automatically detects project root using `justfile` location
- Routes to appropriate directories: src/, tests/
- Uses existing `just lint check` commands
- Shows concise output (first 3 lines of issues only)

#### Search Year Update (`update-search-year.sh`)

- Processes JSON from Claude Code WebSearch tool
- Smart year detection (avoids version numbers, paths)
- Escapes: `@pinned` or `year:exact` queries are left unchanged
- Outputs modified JSON with updated query

## Troubleshooting

### Hooks Not Running

1. **Check Claude Code version**: Hooks require Claude Code 1.0.54+
2. **Verify working directory**: Must be in llm-cli-tools-core project root
3. **Check `/doctor`**: Run `/doctor` in Claude Code to validate hook
   configuration

### Hook Errors

```bash
# Test hooks manually
echo '{"tool_name":"Edit","tool_input":{"file_path":"'$(pwd)'/test.py"}}' | .claude/hooks/lint-on-save.sh

echo '{"tool_name":"WebSearch","tool_input":{"query":"test docs 2024"}}' | .claude/hooks/update-search-year.sh
```

### Disable Hooks Temporarily

Create `.claude/settings.local.json`:

```json
{
  "hooks": {}
}
```

## Advanced Configuration

### Adding Custom Hooks

1. Create script in `.claude/hooks/`
2. Make executable: `chmod +x .claude/hooks/your-hook.sh`
3. Add to `.claude/settings.json` hooks configuration
4. Test manually before committing

### Hook Development

- Hooks receive JSON via stdin from Claude Code
- Must exit with code 0 for success, non-zero to block operation
- Use `jq` to parse JSON input
- Output to stderr for user feedback, stdout for data flow

## Verification

- Run `ls .claude/hooks/` to confirm `lint-on-save.sh` and
  `update-search-year.sh` are present.
- Trigger the lint hook by editing a Python file and confirm the warning format
  matches the example output.
- Run a web search in Claude Code containing an outdated year and verify the
  hook updates the query automatically.

## Performance Guidelines

- **Lint hook**: <500ms execution (0.5s timeout, single file only)
- **Search hook**: <100ms execution (0.1s timeout, regex replacement)
- **Important**: Timeout values are in seconds (use decimals for milliseconds)
- Use timeouts to prevent hanging
- Keep output concise for better UX

## Integration with Existing Workflow

### Works With

- ✅ All existing `just lint` commands
- ✅ All directory-specific linting (src/tests)
- ✅ Global and project-specific Claude settings
- ✅ Justfile-first workflow patterns

### Respects

- ✅ File type restrictions (.py, .ts, .tsx, .js, .jsx)
- ✅ Directory boundaries (src vs tests)
- ✅ Performance constraints (timeouts in seconds, use 0.1 for 100ms)
- ✅ User escape hatches (@pinned searches)

## Team Benefits

- **Immediate feedback**: Catch lint issues as you type
- **Current research**: Always search with recent years
- **Zero config**: Works out of the box for all team members
- **Justfile consistent**: Uses same commands as manual workflow
- **Non-intrusive**: Warns but never blocks your work

---

**Questions?** See
[Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks-guide)
or ask in #engineering Slack.
