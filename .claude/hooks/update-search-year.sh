#!/bin/bash
# .claude/hooks/update-search-year.sh - Project-specific hook

JSON=$(cat)

# Validate JSON input
if ! echo "$JSON" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON input" >&2
    exit 1
fi

TOOL=$(echo "$JSON" | jq -r '.tool_name')

if [[ "$TOOL" != "WebSearch" ]]; then
    echo "$JSON"
    exit 0
fi

QUERY=$(echo "$JSON" | jq -r '.tool_input.query // ""')
CURRENT_YEAR=$(date +%Y)
LAST_YEAR=$((CURRENT_YEAR - 1))

# Skip if contains @pinned or year:exact
if [[ "$QUERY" =~ @pinned|year:exact ]]; then
    echo "$JSON"
    exit 0
fi

# Check for outdated year (last year or older, not part of version/path)
# Matches years from 2010 to last year
if [[ "$QUERY" =~ (^|[^0-9/])(20[1-9][0-9])([^0-9/.]|$) ]]; then
    OLD_YEAR="${BASH_REMATCH[2]}"
    # Only update if the year is older than current year
    if [[ $OLD_YEAR -lt $CURRENT_YEAR ]]; then
        # Use year range for docs, current year for others
        if [[ "$QUERY" =~ (documentation|docs|guide|tutorial|api|reference) ]]; then
            NEW_YEAR="$LAST_YEAR-$CURRENT_YEAR"
        else
            NEW_YEAR="$CURRENT_YEAR"
        fi

        UPDATED_QUERY="${QUERY//$OLD_YEAR/$NEW_YEAR}"
        echo "📅 Updated: $OLD_YEAR → $NEW_YEAR" >&2
        echo "$JSON" | jq --arg q "$UPDATED_QUERY" '.tool_input.query = $q'
    else
        echo "$JSON"
    fi
else
    echo "$JSON"
fi
