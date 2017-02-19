# Takes in a list of hostnames and starts a new tmux session with SSH panes to each of them

session_name="multi-ssh ${@}"

tmux new-session -d -s "${session_name}"
tmux new-window "multi-ssh"
for host in "${@}"; do
    tmux split-window -h "ssh ${host}"
done
tmux select-layout tiled > /dev/null
tmux select-pane -t 0
tmux set-window-option synchronize-panes on > /dev/null
tmux attach
