---
purpose:
  "Set contributor expectations, tooling rules, and workflow guardrails for
  llm-cli-tools-core."
audience: "Contributors, reviewers, automation agents"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# llm-cli-tools-core - Repository Playbook for Claude & Codex

> Shared telemetry utilities for Degree Analytics agents. Use this guide for
> workflow rules, tooling expectations, validation steps, and review readiness.

## 🔑 Project Identity & Principles

- **Justfile-first** - run `just setup`, `just lint`, `just test`, `just ci`,
  and `just docs check` instead of calling `python`, `pytest`, or `uv` directly.
- **GT workflow** - manage branches and PRs with `gt create|modify|submit`.
  Never run `git push`, `git rebase`, or `git merge` manually.
- **TDD mandatory** - propose tests, watch them fail, implement, and repeat
  until the suite is green.
- **Docs stay current** - update `docs/`, `README.md`, and `CONTEXT.md` whenever
  behavior or workflows change.
- **Config-driven storage** - respect `.env` directories and avoid hardcoded
  paths.
- **Git-based distribution** - releases come from git tags; never publish to
  PyPI.

## 🚀 Quick Commands

```bash
just setup            # Bootstrap UV virtual env and dependencies
just lint check       # Ruff lint rules
just lint format      # Auto-format and fix lint issues
just test             # Full test suite (unit + integration)
just test unit        # Unit tests only
just ci               # Lint + tests (mirrors CI)
just docs check       # Markdownlint + cspell + lychee

gt log --stack        # Inspect stack state
gt status             # Verify branch sync before and after work
```

## 🧭 Recommended Workflow

1. **Sync branch with GT**

   ```bash
   gt create --all -m "feat: short summary"
   ```

2. **Install or refresh tooling via Justfile**. Run `just setup` on new
   machines; the target invokes `uv sync` automatically.
3. **Write tests first** under `tests/` to capture the desired behavior.
4. **Implement the feature** in `src/llm_cli_core/` and keep code plus tests in
   the same stack entry.
5. **Validate locally**

   ```bash
   just lint check
   just test
   ```

6. **Update docs** (`docs/`, `README.md`, `CONTEXT.md`, `docs/WORKFLOW.md`) for
   any new workflows or APIs.
7. **Submit via GT**

   ```bash
   gt submit
   ```

8. **Request automated reviews** by mentioning `@codex` and `@claude` as noted
   in `docs/WORKFLOW.md`.

## 🔬 Testing & Verification

- `just test` wraps `uv run pytest` and enforces coverage for
  `src/llm_cli_core`.
- Target suites with `just test unit` or `just test integration`.
- Store coverage artifacts in `.build/coverage/` when needed.
- Regenerate fixtures when telemetry payloads change.
- Run `just ci` before `gt submit` to mirror CI expectations.

## 🗂️ Repository Map

```text
llm-cli-tools-core/
|- docs/            # Documentation index, workflow, and how-to guides
|- scripts/         # Docs validation and supporting tooling
|- src/llm_cli_core/# Library implementation (config, providers, storage,
                    # telemetry)
|- tests/           # Unit and integration suites
|- AGENTS.md        # Cross-agent rules
|- CLAUDE.md        # Canonical workflow guidance
|- justfile         # Development commands (delegating to UV)
```

## 📚 Key References

- [`AGENTS.md`](./AGENTS.md) - cross-agent rules for Claude, Codex, and peers.
- [`docs/WORKFLOW.md`](./docs/WORKFLOW.md) - GT workflow, review etiquette, and
  automation usage.
- [`docs/index.md`](./docs/index.md) - documentation taxonomy and maintenance
  checklist.
- [`docs/development/claude-commands.md`](./docs/development/claude-commands.md)
  - slash-command catalogue.
- [Deployment GT workflow][deployment-gt] - GT guardrails.

## 📦 Distribution & Versioning

- Releases are cut from `main` via GT-managed PRs.
- The `Release` GitHub Action auto-bumps `pyproject.toml` and tags when the
  latest commit on `main` passes CI *and* its message starts with `feat:`/`fix:`
  or includes `BREAKING`.
- Conventional commits still drive the bump level: `feat:` (minor), `fix:`
  (patch), and messages with `BREAKING` trigger a major bump.
- Never edit `pyproject.toml` version fields manually; rely on the automation.

## 💾 Storage & Configuration

- Load storage locations from `.env` (`LLM_TELEMETRY_DIR`, etc.).
- Ensure directories exist before writing and avoid absolute paths.
- Keep telemetry helpers opt-in via `LLM_TELEMETRY_ENABLED` flags.

## ✅ Review Checklist

- [ ] `gt status` and `gt log --stack` are clean before and after work.
- [ ] Tests were written first (red) and `just test` passes locally (green).
- [ ] `just lint check` and `just docs check` succeed.
- [ ] Docs updated for new behaviors, commands, or workflows.
- [ ] No direct `git` commands used during the stack.
- [ ] PR description follows Summary/Testing format and notes telemetry impact.

## 🤖 Slash Commands & Automation

Slash commands map to `.claude/commands/*.md`.

1. Open the command file.
2. Execute the documented `just` or script commands verbatim.
3. Capture outputs or artifacts specified by the command.

## 🧯 Safety & Housekeeping

- Temporary files live in `.build/tmp/`; clean up after use.
- Never commit secrets; copy `.env.example` to `.env` for local runs.
- Respect telemetry toggles when exercising instrumentation.
- Keep the `updated:` metadata current when instructions change.

Keep this guide in sync with `AGENTS.md`; update both whenever workflows
evolve.

[deployment-gt]: ./docs/claude-components/deployment-gt-workflow.md
