#!/usr/bin/env bash

# PreToolUse hook for Bash commands.
#
# Rewrites `git -C <path>` to plain `git` when <path> resolves to the current
# working directory, since the -C flag is redundant in that case.
#
# Why this exists: Claude Code's settings.json permissions can allowlist plain
# git commands (e.g. "Bash(git status *)"), but `git -C <path> status` does not
# match those patterns. Agents — especially subagents spawned via the Task
# tool — frequently add a redundant `-C` flag pointing at the current working
# directory, which causes the command to fall outside the allowlist and trigger
# a permission prompt. By stripping the unnecessary `-C` before execution, the
# command matches the allowlist and runs without interruption.

set -euo pipefail

input="$(cat)"

# Extract the command from the tool input JSON
if ! command -v jq &>/dev/null; then
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
    # Strip the -C and its path argument, collapsing extra whitespace
    rewritten="$(echo "${command_str}" | sed -E "s/git[[:space:]]+-C[[:space:]]+(\"[^\"]+\"|'[^']+'|[^[:space:]]+)[[:space:]]*/git /g")"

    jq -n \
        --arg cmd "${rewritten}" \
        '{
            hookSpecificOutput: {
                hookEventName: "PreToolUse",
                permissionDecision: "allow",
                permissionDecisionReason: "Removed redundant -C flag targeting current directory",
                updatedInput: { command: $cmd }
            }
        }'
    exit 0
fi

# Different directory — no modification needed
exit 0
