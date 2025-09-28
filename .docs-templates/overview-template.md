---
purpose:
  "Document the product overview, install paths, and quick start examples."
audience: "New users, maintainers, stakeholders"
owner: "<team or individual>"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Draft"
---

# {{Project}} Overview

## When to Use This

- Read when evaluating {{Project}} or starting integration.
- Share with partners who need a concise capability tour.

## Prerequisites

- {{Required tooling or access}}
- {{Link to setup instructions}}

## Installation

```bash
just setup
uv pip install "{{package}} @ git+https://github.com/{{org}}/{{repo}}@{{tag}}"
```

## Quick Start

```python
from {{module}} import {{api}}
```

## Optional Features

- **Feature name** — how to enable it.
- **Telemetry/metrics** — environment variables to export.

## Verification

- Run `just test` and confirm the example succeeds.
- Capture outputs or screenshots in release notes if behavior changes.

## Related Docs

- `docs/index.md`
- `{{link to CLI reference}}`
