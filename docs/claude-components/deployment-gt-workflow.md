---
purpose:
  "Define mandatory GT-based workflow rules for code changes and library
  releases."
audience: "Developers, maintainers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# 📦 GT WORKFLOW RULES

**CRITICAL**: Different types of changes follow different workflow paths:

## When to Use This

- Plan or review any changes to the llm-cli-tools-core library that rely on GT
  workflows.
- Audit release readiness before approving main branch merges.

## Prerequisites

- `gt` CLI installed and authenticated.
- Valid Python environment with UV for local testing.

## Code Changes (src/, tests/)

1. **ALWAYS use GT workflow** → Create branch → PR to dev → Test → PR to main
2. **NEVER deploy code directly** to production without PR review
3. **Workflow**:

   ```bash
   gt create --all -m "fix: description"  # Create branch
   gt submit                              # Create PR to dev
   # After dev testing and approval
   gt checkout main && gt sync            # Switch to main
   gt create --all -m "merge: dev to main" # Create merge branch
   gt submit                              # Create PR to main
   ```

## Library Changes (Config, Dependencies)

1. **All changes**: Follow code workflow (PR required)
2. **Examples**:
   - Updating dependencies in pyproject.toml → PR workflow
   - Changing configuration defaults → PR workflow
   - Adding new telemetry providers → PR workflow

## GT ESSENTIALS (Minimal Reminders)

**Core Rule**: Use `gt` for branches, never `git`

- Before ANY operation: `git status && gt log --stack`

## 🚨 CRITICAL GT RESTACK RULES

**NEVER use rebase during gt restack operations!**

- When `gt restack` shows merge conflicts → Use merge resolution, NOT rebase
- FORBIDDEN: `git rebase` during any GT workflow
- REQUIRED: Let GT handle the merge strategy
- If tempted to rebase → STOP and ask user for guidance
- Rebase breaks GT's internal tracking and causes cascading conflicts

## Verification

- Capture `gt status` and `gt log --stack` output before and after the
  deployment sequence to confirm history integrity.
- Ensure both dev and main PRs show successful CI runs prior to merging.
