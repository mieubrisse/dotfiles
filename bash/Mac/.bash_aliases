# ls conveniences
function ls() { # Display an empty line for empty directories
    if [[ $(/bin/ls $@ | wc -l) -eq 0 ]]; then
        echo 
    else
        /bin/ls -G "$@"
    fi
}
alias ll='ls -AlhF'
alias lld='ll -c' # Sort by date last modified
alias la='ls -A'
alias l='ls -CF'

# Make find not suck
alias cif="find . -iname" # Case-insensitive find
function ff() { # Fuzzy find
    # echo "INSIDE FUZZY FIND"
    SEARCH_STR="$1"
    shift 1
    cif "*$SEARCH_STR*" "$@"
}

# Breaks a command result by newline and gives option which to copy
# E.g. 'coolcp ls' would give the option of copying one of the ls results
# Handles piped input, so 'ls | coolcp' accomplishes the same as the above
function coolcp {
    # If it exists, read data from stdin to handle piped input
    if [ "$(tty)" == 'not a tty' ]; then
        while IFS='' read -r LINE; do
            ITEM_ARR+=("$LINE")
        done

    # Otherwise, perform the command the user specifies
    else
        COMMAND="$1"
        shift 1
        ITEM_ARR=($("$COMMAND" "$@"))
    fi

    ARR_SIZE="${#ITEM_ARR[@]}"
    if [[ "$ARR_SIZE" -gt 1 ]]; then
        for idx in "${!ITEM_ARR[@]}"; do
            printf "%s\t%s\n" "$idx" "${ITEM_ARR[$idx]}"
        done
        read -p "Copy which? " TARGET_IDX </dev/tty
        TARGET_ITEM="${ITEM_ARR[$TARGET_IDX]}"
    elif [[ "$ARR_SIZE" -eq 1 ]]; then
        TARGET_ITEM="${ITEM_ARR[0]}"
    else
        echo "No results to copy"
        return
    fi
    echo "Copied $TARGET_ITEM to clipboard"
    echo "target: $TARGET_ITEM"
    printf "$TARGET_ITEM" | sed "s:\x1B\[[0-9;]*[mK]::g" | pbcopy
}

# Source .bashrc for convenience
alias srcbash=". ~/.bashrc"

# Make directory and cd into it
function mkdcd() { mkdir "$@"; cd "$1"; }

# Color grep
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias gr='grep'
alias grr='grep -r'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Map command to open last vim session
alias   v="vim"
VIM_SESSION="~/.vim/.saved-session.vim"
alias   vims="vim -S $VIM_SESSION"

# Jobs should show PID by default
alias   jobs="jobs -l"

# Quickly manage Palantir quickstarts
alias   quickchange="/Users/ktoday/scripts/quickchange/quickchange"

# Don't want to make srm too easy to use!
# alias srm="srm -i"

# Rebind 'cd' to list contents after changing directory 
# function cd() { builtin cd "${@:-$HOME}" && ls; }

# Shorter Git commands
alias ga="git add"
alias gs="git status"
alias gl1="git log --graph --abbrev-commit --decorate --date=relative --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)' --all"
alias gl2="log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold cyan)%aD%C(reset) %C(bold green)(%ar)%C(reset)%C(bold yellow)%d%C(reset)%n''          %C(white)%s%C(reset) %C(dim white)- %an%C(reset)' --all"
alias gcm="git commit"
alias gcl="git clone"
alias gco="git checkout"

# Output redirection functions
function    unify_output() { 2>&1 "${@}"; }
function    quiet() { "${@}" 2> /dev/null; }
function    silent() { "${@}" > /dev/null 2>&1; }

# Better diff
alias   diff="colordiff -u"

