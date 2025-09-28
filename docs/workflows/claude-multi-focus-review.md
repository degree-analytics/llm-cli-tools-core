---
purpose:
  "Document the deprecated multi-focus review workflow and point to the
  replacement."
audience: "Contributors maintaining historical workflows"
owner: "Core AI Tools"
review: "As needed when workflows change"
status: "Deprecated"
---

# Claude Multi-Focus Review (Deprecated)

**This workflow has been simplified!**

Please see [Claude Review Workflows](./claude-review-workflows.md) for the new
streamlined approach.

## When to Use This

- Only when auditing historical runs or understanding legacy automation
  decisions.

## Prerequisites

- None. Use the replacement workflow for active reviews.

## What Changed

We consolidated from multiple separate workflows to a single unified workflow
with 2 review sections:

- **Technical Review**: Architecture, security, testing, functionality
- **Standards Review**: Documentation, patterns, conventions, justfile

This simplification:

- Provides all feedback in one comprehensive comment
- Fixes the 40k character repository issue
- Uses the proven `custom_instructions` approach that actually works
- Triggered only by `@claude` comments (not automatic on every PR)
- Easier to maintain and debug

## Verification

- Confirm `.github/workflows/claude.yml` has replaced any references to the
  multi-focus workflow before removing this document.
