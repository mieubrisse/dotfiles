#!/bin/bash
set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"

# Template patterns
TITLE_PREFIX="TITLE:"
BODY_PREFIX="BODY (below):"

# Get title from command line arguments
title_args="$*"

# Create a temporary file for editing
temp_file=$(mktemp)

# Add the template content
cat > "${temp_file}" << EOF
${TITLE_PREFIX} ${title_args}
${BODY_PREFIX}
EOF

# Open the editor
${EDITOR:-vim} "${temp_file}"

# Parse the file
title=""
body=""
in_body=false

while IFS= read -r line; do
    if [[ "${line}" =~ ^${TITLE_PREFIX}(.*)$ ]]; then
        title="${BASH_REMATCH[1]}"
        title="${title# }"  # Remove leading space if present
    elif [[ "${line}" =~ ^${BODY_PREFIX} ]]; then
        in_body=true
        # Get any text after the body prefix on the same line
        body_start="${line#${BODY_PREFIX}}"
        body_start="${body_start# }"  # Remove leading space if present
        if [[ -n "${body_start}" ]]; then
            body="${body_start}"
        fi
    elif [[ "${in_body}" == true ]]; then
        if [[ -n "${body}" ]]; then
            body="${body}"$'\n'"${line}"
        else
            body="${line}"
        fi
    fi
done < "${temp_file}"

# Clean up temp file
rm "${temp_file}"

# Check if title is provided
if [[ -z "${title}" ]]; then
    echo "Error: No title provided" >&2
    exit 1
fi

# Create the GitHub issue
if [[ -n "${body}" ]]; then
    gh issue create --title "${title}" --body "${body}"
else
    gh issue create --title "${title}"
fi
