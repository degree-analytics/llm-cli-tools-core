#!/bin/bash
# .claude/hooks/lint-on-save.sh - Project-specific hook

JSON=$(cat)
TOOL=$(echo "$JSON" | jq -r '.tool_name')

# Only run for file modifications
if [[ "$TOOL" =~ ^(Edit|Write|MultiEdit)$ ]]; then
    FILE=$(echo "$JSON" | jq -r '.tool_input.file_path')

    # Skip if not a code file
    if [[ ! "$FILE" =~ \.(py|ts|tsx|js|jsx)$ ]]; then
        exit 0
    fi

    # Find project root (where justfile exists)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    cd "$PROJECT_ROOT" || exit

    if [[ "$FILE" == */apps/backend/* ]] && [[ "$FILE" == *.py ]]; then
        OUTPUT=$(just lint check backend --files "$FILE" 2>&1 || true)

    elif [[ "$FILE" == */apps/admin/* ]]; then
        OUTPUT=$(just lint check admin --files "$FILE" 2>&1 || true)

    elif [[ "$FILE" == */apps/mobile/* ]]; then
        OUTPUT=$(just lint check mobile --files "$FILE" 2>&1 || true)

    elif [[ "$FILE" == */scripts/* ]]; then
        OUTPUT=$(just lint check scripts --files "$FILE" 2>&1 || true)

    else
        exit 0  # Skip files outside main areas
    fi

    # Only show output if there are issues
    if [[ -n "$OUTPUT" ]] && [[ "$OUTPUT" != *"✅"* ]] && [[ "$OUTPUT" != *"All checks passed"* ]]; then
        echo "⚠️  $(basename "$FILE"):"
        echo "$OUTPUT" | head -3  # Keep it concise
    fi
fi

exit 0  # Never block saves
