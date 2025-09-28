---
purpose:
  "Provide a single entry point and taxonomy for llm-cli-tools-core
  documentation."
audience: "Contributors, maintainers, reviewers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# Documentation Index

This index maps the shared documentation taxonomy and highlights the status of
each asset. Every document should begin with the standard metadata block and
follow the templates in `.docs-templates/`.

## Doc Types

### Overview & Quickstart

- **Primary Docs:** [README.md](../README.md), [CONTEXT.md](../CONTEXT.md)
- **Status:** Active
- **Notes:** Product summary, install paths, current capabilities.

### Contributor Guide

- **Primary Docs:** [CLAUDE.md](../CLAUDE.md)
- **Status:** Active
- **Notes:** Mandatory workflow, tooling, and review standards.

### Architecture & Context

- **Primary Docs:** [CONTEXT.md](../CONTEXT.md),
  [docs/development/claude-context-management.md](development/claude-context-management.md)
- **Status:** Active
- **Notes:** Problem framing, context hierarchy, inheritance model.

### How-to / Runbooks

- **Primary Docs:**
  [docs/development/claude-hooks-setup.md](development/claude-hooks-setup.md),
  [docs/development/github-app-integration.md](development/github-app-integration.md)
- **Status:** Active
- **Notes:** Step-by-step procedures with verification guidance.

### CLI / Command Reference

- **Primary Docs:** [docs/development/claude-commands.md](development/claude-commands.md)
- **Status:** Active
- **Notes:** Slash-command catalogue and usage examples.

### Policies & Standards

- **Primary Docs:**
  [docs/claude-components/deployment-gt-workflow.md](claude-components/deployment-gt-workflow.md)
- **Status:** Active
- **Notes:** Non-negotiable deployment rules and guardrails.

### Workflow Runbooks

- **Primary Docs:**
  [docs/workflows/claude-review-workflows.md](workflows/claude-review-workflows.md)
- **Status:** Active
- **Notes:** GitHub and local automation guidance.

### Deprecated Assets

- **Primary Docs:**
  [docs/workflows/claude-multi-focus-review.md](workflows/claude-multi-focus-review.md)
- **Status:** Deprecated
- **Notes:** Redirects to `claude-review-workflows.md`.

## Templates & Conventions

- Template sources: `.docs-templates/` (overview, contributor, architecture,
  how-to, CLI, policy).
- Metadata block keys (all required): `purpose`, `audience`, `owner`, `review`,
  `status`.
- Each document must include **When to Use This**, **Prerequisites**, and
  **Verification** sections when applicable.

## Maintenance Checklist

- Run `just docs check` (markdownlint + cspell + lychee) before merging
  documentation changes.
- Ensure Node.js 18+ and a Rust toolchain (lychee) are available locally to run
  `scripts/docs_phase2.sh`.
- Update the `owner` and `review` fields when ownership changes.
- Mark deprecated docs with `status: Deprecated` and link to the replacement.

## Pending Gaps

- Add onboarding walkthrough once the shared telemetry workflow is finalized.

## Frontmatter fields

| Field     | Purpose                                      | Notes                          |
|-----------|----------------------------------------------|--------------------------------|
| `purpose` | One-line statement of why the doc exists      | Displayed at top of documents  |
| `audience`| Primary readers (roles/teams)                 | Guides tone and depth          |
| `owner`   | Accountable individual or team                | Update when stewardship shifts |
| `review`  | Planned review cadence (e.g., Quarterly)      | Drives doc hygiene reminders   |
| `status`  | Active / Draft / Deprecated lifecycle         | Signals whether doc is current |

## Docs validation configuration

The docs tooling reads environment variables (set via the shell or a `.env` file) to override defaults:

- `DOCS_CSPELL_FILES` – files/globs passed to cspell
- `DOCS_LYCHEE_FILES` – files/globs passed to lychee
- `DOCS_LYCHEE_ARGS` – additional lychee arguments
- `DOCS_CSPELL_CONFIG` – alternate cspell config path
- `DOCS_LYCHEE_CONFIG` – alternate lychee config path
- `DOCS_LYCHEE_VERSION` – required lychee version (default `0.13.0`)

Use these overrides sparingly; the CI workflow runs with the defaults defined in `scripts/docs_phase2.sh`.

## Release notes

- Release automation bumps versions when commits merged to `main` use a `feat:`
  or `fix:` prefix.
- Include documentation-impacting changes in those commits when they should
  appear in the generated changelog.
