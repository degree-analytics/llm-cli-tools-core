---
purpose:
  "Document the end-to-end contributor workflow for llm-cli-tools-core, aligning
  Claude and Codex automation with GT and TDD guardrails."
audience: "Contributors, reviewers, automation agents"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# llm-cli-tools-core Workflow Playbook

## When to Use This

Consult this playbook whenever you:

- Spin up a new feature or bugfix branch.
- Need a refresher on TDD expectations or verification gates.
- Prepare to submit work through the GT workflow.

## Prerequisites

- `gt` CLI installed and authenticated.
- Local environment bootstrapped with `just setup`.
- Ability to run `just docs check` (Node 18+ and Rust toolchain for lychee).

## 🧭 GT Branch Management

```bash
gt create --all -m "feat: short summary"      # Start a new stack entry
gt log --stack                                 # Inspect current stack
gt modify --all                                 # Amend later commits if needed
gt submit                                       # Open PR with CI hooks
```

### Rules

- Never run `git push`, `git rebase`, or `git merge` manually.
- Resolve conflicts through GT prompts. If `gt restack` appears, follow
  `.claude/agents/gt-restack-expert.md`.
- Capture `gt status` output before and after major operations when debugging.

## 🔁 TDD Loop

1. Draft or update a failing test under `tests/unit/` or `tests/integration/`.
2. Run the relevant suite (`just test unit` or `just test integration`).
3. Implement the smallest change in `src/llm_cli_core/` to make it pass.
4. Repeat until the red to green cycle completes.
5. Run `just test` to ensure the full suite stays green.

### Guidelines

- Prefer unit tests for pure functions and integration tests for storage or
  telemetry paths.
- Keep fixtures alongside tests; document new fixtures within the test module.

## 🛠️ Justfile Cheat Sheet

- `just setup` - create the UV virtual environment and sync dependencies.
- `just test` - run the full suite with coverage reporting.
- `just test unit` / `just test integration` - target specific suites.
- `just lint check` - apply Ruff lint rules.
- `just lint format` - auto-fix formatting and lint issues.
- `just docs check` - run markdownlint, cspell, and lychee.
- `just ci` - execute lint and the full test suite (mirrors CI).

## ✅ Pre-Submit Verification

- [ ] `just lint check` passes with no modifications needed.
- [ ] `just test` (or targeted suite plus full run) completes successfully.
- [ ] `just docs check` succeeds when documentation changed.
- [ ] `gt status` is clean and `gt log --stack` shows expected order.
- [ ] Docs updated for workflow or API changes (`README.md`, `CONTEXT.md`,
  `docs/`).
- [ ] Commit messages follow Conventional Commits. Include `BREAKING CHANGE:`
  when required.

## 🤖 Automation & Slash Commands

- Slash commands live in `.claude/commands/`. Open the command file, execute the
  documented steps, and return the requested artifacts.
- Use `@.claude/commands/<name>` syntax when referencing files directly within
  Claude or Codex sessions.
- Shared automation (ground truth, docs hygiene) resides under `scripts/`.
  Prefer invoking these helpers via `just` targets.

## 📚 Related Docs

- [`CLAUDE.md`](../CLAUDE.md) - Canonical repository guidance.
- [`AGENTS.md`](../AGENTS.md) - Cross-agent expectations and quick references.
- [`docs/index.md`](./index.md) - Documentation taxonomy and maintenance rules.
- [Deployment GT workflow][workflow-gt] - GT deployment guardrails.
- [`docs/development/claude-commands.md`](./development/claude-commands.md) -
  Slash command catalogue.

## Verification

- Run `just ci` before `gt submit` to ensure lint and test status matches CI.
- Attach relevant command outputs (for example `just test`, `gt status`) to
  review or PR comments when requested.

Maintain this playbook in lockstep with workflow changes or new automation.

[workflow-gt]: ./claude-components/deployment-gt-workflow.md
