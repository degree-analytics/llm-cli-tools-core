---
purpose: "Runbook for triggering and interpreting Claude-powered PR reviews."
audience: "Developers, reviewers, release managers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# Claude Review Workflows

SpaceWalker uses Claude for automated code reviews on PRs via GitHub comments
(official action) and optional local tools.

## When to Use This

- Request AI-assisted code reviews directly in GitHub pull requests.
- Compare local analysis versus hosted review outputs before merging.

## Prerequisites

- Repository secret `ANTHROPIC_API_KEY` populated.
- Optional model override variables configured when deviating from defaults.

What’s new

- Official action: anthropics/claude-code-action@v1
- Targeted categories: docs, justfile, correctness, overengineering
- Multi-select: “review docs, justfile” or “review all”
- Sticky comments: single sticky per category when run individually; separate
  category metrics when multiple run together
- Metrics: model, token counts, and estimated cost per run

Secrets, variables, and defaults

- Required secret: ANTHROPIC_API_KEY – Optional repo variables (models):
  - CLAUDE_MODEL_DOCS, CLAUDE_MODEL_JUSTFILE, CLAUDE_MODEL_CORRECTNESS,
    CLAUDE_MODEL_OVERENGINEERING, CLAUDE_MODEL_DEFAULT
  - Defaults: all categories → claude-4-1-sonnet-20250805 (set
    CLAUDE_MODEL_HAIKU or category-specific variables to override)
- Optional costs:
  - Preferred: CLAUDE_COSTS_JSON (JSON map of model → { in, out })
  - Fallback file: .github/claude-costs.json (checked in with real rates)
  - Global fallback: CLAUDE_INPUT_COST_PER_MTOK, CLAUDE_OUTPUT_COST_PER_MTOK

GitHub-triggered usage

- Comment on the PR (top-level or inline):
  - “@claude review docs” or “/claude review docs”
  - “@claude review justfile” or “/claude review justfile”
  - “@claude review correctness” or “/claude review correctness”
  - “@claude check overengineering” or “/claude check overengineering”
  - “@claude review all” or “/claude review all” (runs all four)

Review outputs

- Category review comment(s) with findings and next actions
- Sticky metrics comment per category: model, input/output tokens, estimated
  cost, run link

Implementation

- Workflow: .github/workflows/claude.yml
- Official action: v1
- Category prompts enforce CLAUDE.md standards, Justfile-first patterns, and
  SpaceWalker rules
- Multi-category runs avoid single-comment collisions by posting
  category-specific outputs and metrics

## Verification

- Trigger `/claude review docs` on a sample PR and confirm the workflow posts
  category-specific comments and metrics.
- Review the sticky metrics comment to ensure token and cost values populate as
  expected.

Local PR analysis (optional)

- For quick, local insights during development:

```bash
# Complete PR review with AI analysis (summary)
just git-info pr-review-issues 290 --analysis=summary

# Quick PR summary
just gh-pr 290 --format=summary

# AI risk assessment
just git-info pr-review-issues 290 --analysis=risk

# Just the PR title
just gh-pr 290 --format=title

# Analyze PR from different repository
just gh-pr 290 --repo=other/repo
```

### Key Differences from GitHub Reviews

| Feature | GitHub (`@claude`) | Local (`just gh-pr`)        |
| ------- | ------------------ | --------------------------- |
| Trigger | PR comment         | Command line                |
| Speed   | ~2-5 minutes       | Immediate                   |
| Results | Posted to PR       | Terminal output             |
| Model   | Claude Opus 4      | Claude Haiku (configurable) |
| Scope   | Full PR diff       | Targeted analysis           |

### When to Use Each

**Use GitHub Reviews (`@claude`) when:**

- You want review results documented in the PR
- Multiple team members need to see the analysis
- You're doing a final review before merge
- You need deep, comprehensive analysis

**Use Local Analysis (`just gh-pr`) when:**

- You need quick insights during development
- You're iterating on PR feedback
- You want to check specific aspects (risk, test status)
- You're reviewing multiple PRs quickly

### Available Local Commands

```bash
# Full review (3 sections: overview, AI analysis, test status)
just git-info pr-review-issues <pr_number>

# Individual analyses
just git-info pr-review-issues <pr_number> --analysis=summary \
  # Comprehensive AI review
just git-info pr-review-issues <pr_number> --analysis=comments \
  # Comment thread analysis
just git-info pr-review-issues <pr_number> --analysis=risk \
  # Risk assessment
just git-info pr-review-issues <pr_number> --analysis=test-freshness \
  # Test timing analysis

# Actionable, time-aware list (new)
just git-info pr-review-issues <pr_number> --analysis=actionable \
  --since-last-push

# Data commands
just gh-pr fetch <pr_number>            # Raw PR data (JSON)
just gh-pr format <pr_number> summary   # Human-readable summary
just gh-pr test-status <pr_number>      # CI/CD check status
```

Troubleshooting

- Not triggering: ensure @claude appears in a PR comment (not issues), and you
  have write access
- No metrics cost: set CLAUDE_COSTS_JSON or update .github/claude-costs.json
- Wrong model: set the category model variables above

Related docs

- Codex Reviewer: see ./codex-review-workflows.md
- PR Analysis Guide: ./pr-analysis-guide.md
