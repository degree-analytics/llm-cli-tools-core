# llm-cli-tools-core Agent Guide

## Purpose
Unify expectations for Claude, Codex, Cursor, Windsurf, and other IDE assistants
when contributing to llm-cli-tools-core. Treat `CLAUDE.md` as the canonical
source of workflow rules.

## Core Rules
- **Read `CLAUDE.md` first** every session; follow its quick commands and review
  checklist.
- **Justfile-first**: run `just setup`, `just lint`, `just test`, `just ci`, and
  `just docs check` instead of calling `python`, `pytest`, or `uv` directly.
- **GT workflow**: manage branches and PRs using `gt create`, `gt modify`, and
  `gt submit`. Never run `git push`, `git rebase`, or `git merge` manually.
- **TDD by default**: add or update tests before implementing feature code.
- **Temp files**: write transient artefacts to `.build/tmp/` only so CI remains
  consistent.
- **Conventional commits/PRs**: use `feat:`, `fix:`, `chore:`, etc., and include
  Summary/Testing sections in PR bodies.
- **Release automation**: commits merged into `main` with `feat:`/`fix:` prefixes
  or `BREAKING` in the message trigger the `Release` workflow to bump versions
  and tag automatically.

## Slash Commands & Automation
- Slash commands map to `.claude/commands/*.md`. Open the command file, execute
  the documented `just` or helper scripts, and preserve any output requirements.
- Example usages:
  - `/ground-truth "CSRF authentication"`
  - `/ground-truth "JWT token handling"`
  - `/ground-truth "user registration flow"`

## Repository Map
- **Library implementation**: `src/llm_cli_core/` (config, providers, storage,
  telemetry).
- **Docs**: `docs/` (see `docs/index.md`, `docs/WORKFLOW.md`,
  `docs/workflows/`).
- **Tests & fixtures**: `tests/` (unit + integration).
- **Automation**: `justfile`, `scripts/`, `.claude/commands/`.

## Development Workflow (All Agents)
1. Sync branches with `gt create` (or `gt modify` in a stack).
2. Use `just setup` once per machine, then rely on `just lint`, `just test`, and
   `just ci` before committing.
3. Propose tests first, implement changes, and re-run `just test` until green.
4. Update docs or roadmaps when behaviour, APIs, or workflows change.
5. Submit using `gt submit` and request review by tagging `@codex` and
   `@claude` when applicable.

## Additional References
- [`CLAUDE.md`](./CLAUDE.md) - canonical repo guidance.
- [`docs/WORKFLOW.md`](./docs/WORKFLOW.md) - detailed GT workflow, review
  process, and automation etiquette.
- `.claude/commands/` - slash command definitions.

Keep this document aligned with `CLAUDE.md`; update both when workflows or tools
change.
