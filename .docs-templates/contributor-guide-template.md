---
purpose: "Describe contributor expectations, workflows, and guardrails."
audience: "Contributors, reviewers, release managers"
owner: "<team or individual>"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Draft"
---

# {{Repository}} Contributor Guide

## When to Use This

- Review before opening PRs or shipping releases.
- Reference during code review for workflow questions.

## Core Principles

1. **{{Rule name}}** — why the rule exists.
2. **{{Rule name}}** — what to do instead of the anti-pattern.

## Prerequisites

- Access to required secrets or org membership.
- Local environment configured with `just setup`.

## Development Workflow

1. Create branch with `gt create --all -m "feat: summary"`.
2. Write tests before implementation.
3. Run `just ci` prior to committing.
4. Submit PR with checklist filled.

## Tooling Commands

```bash
just setup
just lint check
just test all
just docs check
```

## Verification & Sign-off

- Capture test output for major changes.
- Update documentation when behavior changes.

## Related Docs

- `CLAUDE.md`
- `docs/index.md`
