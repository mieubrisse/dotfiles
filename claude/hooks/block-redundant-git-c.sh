#!/usr/bin/env bash

# PreToolUse hook for Bash commands.
# Blocks `git -C <path>` when <path> resolves to the current working directory,
# since the -C flag is redundant in that case.

set -euo pipefail

input="$(cat)"

# Extract the command from the tool input JSON
if ! command -v jq &>/dev/null; then
    # Can't parse JSON without jq; no opinion
    exit 0
fi

command_str="$(echo "${input}" | jq -r '.tool_input.command // empty')"

if [ -z "${command_str}" ]; then
    exit 0
fi

# Check if this is a git command with -C flag
if ! echo "${command_str}" | grep -qE '(^|[;&|]\s*)git\s+-C\s'; then
    exit 0
fi

# Extract the path argument after -C
# Handles: git -C /some/path ..., git -C "/some/path" ..., git -C '/some/path' ...
c_path="$(echo "${command_str}" | sed -nE 's/.*git[[:space:]]+-C[[:space:]]+("([^"]+)"|'\''([^'\'']+)'\''|([^[:space:]]+)).*/\2\3\4/p' | head -1)"

if [ -z "${c_path}" ]; then
    exit 0
fi

# Expand ~ to HOME
c_path="${c_path/#\~/${HOME}}"

# Resolve both paths to canonical form
resolved_c_path="$(cd "${c_path}" 2>/dev/null && pwd -P)" || exit 0
resolved_pwd="$(pwd -P)"

# Strip trailing slashes
resolved_c_path="${resolved_c_path%/}"
resolved_pwd="${resolved_pwd%/}"

if [ "${resolved_c_path}" = "${resolved_pwd}" ]; then
    reason="git -C is pointing to the current working directory (${resolved_pwd}), making the -C flag redundant. Remove -C and run git directly."
    echo "{\"decision\":\"block\",\"reason\":$(echo "${reason}" | jq -Rs '.')}"
    exit 0
fi

# Different directory — allow it
exit 0
