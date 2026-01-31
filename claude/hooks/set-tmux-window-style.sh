#!/usr/bin/env bash

# Sets or unsets the window-status-style on the tmux window where this
# process is running. Used by Claude Code hooks to visually indicate
# whether Claude is actively working.
#
# Usage:
#   set-tmux-window-style.sh 'bg=blue,fg=white,bold'   # set style
#   set-tmux-window-style.sh --unset                    # remove override

set -euo pipefail

# Exit gracefully if not running inside tmux
[ -n "${TMUX:-}" ] || exit 0

window_id=$(tmux display-message -p -t "${TMUX_PANE}" '#{window_id}')

if [ "${1:-}" = "--unset" ]; then
    tmux set-option -wu -t "${window_id}" window-status-style
else
    tmux set-option -w -t "${window_id}" window-status-style "${1}"
fi
