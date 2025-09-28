#!/usr/bin/env bash
set -euo pipefail

# Docs validation configuration can be overridden via environment variables
# (see docs/index.md for the list of supported DOCS_* options).

: "${DOCS_CSPELL_FILES:=README.md CLAUDE.md CONTEXT.md docs/**/*.md .docs-templates/*.md}"
: "${DOCS_LYCHEE_FILES:=README.md CLAUDE.md CONTEXT.md docs/**/*.md}"
: "${DOCS_LYCHEE_ARGS:=--max-concurrency 4 --timeout 20 --retry-wait-time 2 --no-progress}"
: "${DOCS_CSPELL_CONFIG:=cspell.config.yaml}"
: "${DOCS_LYCHEE_CONFIG:=lychee.toml}"

if ! command -v npx >/dev/null 2>&1; then
  echo "❌ npx not found. Install Node.js 18+ to run spell checking." >&2
  exit 1
fi

if [ ! -f "$DOCS_CSPELL_CONFIG" ]; then
  echo "ℹ️  Generating default cspell config at $DOCS_CSPELL_CONFIG" >&2
  cat <<'CFG' > "$DOCS_CSPELL_CONFIG"
version: "0.2"
language: en
words:
  - Mímir
  - openrouter
  - pushgateway
  - Pushgateway
  - PUSHGATEWAY
  - overengineering
  - justfile
  - automations
  - dataclass
  - Groundtruth
  - Claude
  - Spacewalker
  - pytest
  - pyproject
  - chadwalters
  - getenv
  - commandname
  - fastapi
  - Runbook
  - anthropics
  - MTOK
flagWords: []
ignorePaths:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/dist/**"
  - "**/.cache/**"
CFG
fi

echo "🧡 Running cspell…"
npx --yes cspell@7.2.0 lint --config "$DOCS_CSPELL_CONFIG" $DOCS_CSPELL_FILES

echo "🌐 Running lychee…"
MIN_LYCHEE_VERSION=${DOCS_LYCHEE_VERSION:-0.13.0}
MAX_LYCHEE_VERSION=${DOCS_LYCHEE_MAX_VERSION:-0.14.0}

if ! command -v lychee >/dev/null 2>&1; then
  echo "❌ lychee not found. Install via: cargo install lychee --version ${MIN_LYCHEE_VERSION}" >&2
  exit 1
fi

installed=$(lychee --version | awk '{print $2}')
version_ge() {
  printf '%s
' "$1" "$2" | sort -V | tail -n1 | grep -qx "$2"
}
version_lt() {
  [ "$1" = "$2" ] && return 1
  printf '%s
' "$1" "$2" | sort -V | head -n1 | grep -qx "$1"
}
if ! version_ge "$installed" "$MIN_LYCHEE_VERSION"; then
  echo "❌ lychee >= $MIN_LYCHEE_VERSION required (found $installed). Reinstall with: cargo install lychee --version $MIN_LYCHEE_VERSION" >&2
  exit 1
fi
if ! version_lt "$installed" "$MAX_LYCHEE_VERSION"; then
  echo "❌ lychee versions >= $MAX_LYCHEE_VERSION are not yet validated (found $installed). Pin to: cargo install lychee --version $MIN_LYCHEE_VERSION" >&2
  exit 1
fi

if [ -f "$DOCS_LYCHEE_CONFIG" ]; then
  lychee --config "$DOCS_LYCHEE_CONFIG" $DOCS_LYCHEE_ARGS $DOCS_LYCHEE_FILES
else
  lychee $DOCS_LYCHEE_ARGS $DOCS_LYCHEE_FILES
fi

echo "✅ Phase 2 docs checks complete."
