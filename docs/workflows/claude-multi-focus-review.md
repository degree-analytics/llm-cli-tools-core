# Claude Multi-Focus Review (Deprecated)

**This workflow has been simplified!**

Please see [Claude Review Workflows](./claude-review-workflows.md) for the new streamlined approach.

## What Changed

We consolidated from multiple separate workflows to a single unified workflow with 2 review sections:
- **Technical Review**: Architecture, security, testing, functionality
- **Standards Review**: Documentation, patterns, conventions, justfile

This simplification:
- Provides all feedback in one comprehensive comment
- Fixes the 40k character repository issue  
- Uses the proven `custom_instructions` approach that actually works
- Triggered only by `@claude` comments (not automatic on every PR)
- Easier to maintain and debug