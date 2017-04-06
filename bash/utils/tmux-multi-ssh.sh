# Takes in a list of hostnames and starts a new tmux session with SSH panes to each of them

session_name="multi-ssh - $(date +"%FT%H%M%S")"

if [ "${#}" -eq 0 ]; then
    echo -n "Error: Provide a list of hosts to SSH to" >&2
    exit 1
fi

hosts=( "${@}" )

tmux new-session -d -s "${session_name}"
tmux new-window "ssh ${hosts[0]}"
unset hosts[0];
for i in "${hosts[@]}"; do
    tmux split-window -h  "ssh $i"
done
tmux select-layout tiled
tmux select-pane -t 0
tmux set-window-option synchronize-panes on > /dev/null
tmux attach
