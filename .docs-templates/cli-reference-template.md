---
purpose: "Document CLI surface area, arguments, and examples."
audience: "CLI users, automation engineers"
owner: "<team or individual>"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Draft"
---

# {{Project}} CLI Reference

## When to Use This

- Running commands from terminals, scripts, or CI pipelines.
- Validating CLI changes during reviews.

## Prerequisites

- Install {{Project}} via `uv pip install ...`.
- `just setup` completed locally.

## Commands

### {{Command}}

Purpose: what the command does.

```bash
{{binary}} {{command}} --flag value
```

Options:

- `--flag` — description (default: value)

### {{Next Command}}

Purpose: what the command does.

```bash
{{binary}} {{next}}
```

## Configuration

```yaml
key: value
```

## Verification

- Sample output or log snippet.
- Tests to run when flags change.

## Related Docs

- `README.md`
- `docs/index.md`
