#!/usr/bin/env bash

# Creates necessary directories & symlinks
# NOTE: this is idempotent; it's fine to rerun multiple times

set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"

vim_dirpath="${HOME}/.vim"
ipython_dirpath="${HOME}/.ipython/profile_default"
claude_dirpath="${HOME}/.claude"
karabiner_config_dirpath="${HOME}/.config/karabiner"

# Create various needed directories
dirpaths_to_create=(
    "${vim_dirpath}"
    "${ipython_dirpath}"
    "${claude_dirpath}"
)
for dirpath in "${dirpaths_to_create[@]}"; do
    mkdir -p "${dirpath}"
done

# Big array of symlinks to create in the form (source,link to create)
symlink_arr=(
    "${script_dirpath}/bash/bash_aliases,${HOME}/.bash_aliases"
    "${script_dirpath}/bash/bash_logout,${HOME}/.bash_logout"
    "${script_dirpath}/bash/bashrc,${HOME}/.bashrc"
    "${script_dirpath}/git/gitconfig,${HOME}/.gitconfig"
    "${script_dirpath}/vim,${HOME}/.vim"
    "${script_dirpath}/bash/utils,${HOME}/.bash_utils"
    "${script_dirpath}/bash/editrc,${HOME}/.editrc"
    "${script_dirpath}/tmux/tmux.conf,${HOME}/.tmux.conf"
    "${HOME}/.bashrc,${HOME}/.bash_profile"
    "${vim_dirpath}/vimrc,${HOME}/.vimrc"
    "${script_dirpath}/ipython/ipython_config.py,${ipython_dirpath}/ipython_config.py"
    "${script_dirpath}/intellij-idea/ideavimrc,${HOME}/.ideavimrc"
    "${script_dirpath}/fd/fdignore,${HOME}/.fdignore"
    "${HOME}/Google Drive/My Drive,${HOME}/gdrive" # Google Drive
    "${script_dirpath}/karabiner,${karabiner_config_dirpath}" # Karabiner config
    "${script_dirpath}/claude/CLAUDE.md,${claude_dirpath}/CLAUDE.md"
    "${script_dirpath}/hushlogin,${HOME}/.hushlogin"
    "${script_dirpath}/overpowered-writing/overpowered-writing.env,${HOME}/.overpowered-writing.env"
)

for link_def in "${symlink_arr[@]}"; do
    source_filepath="$(echo "${link_def}" | cut -d',' -f1)"
    if ! [ -e "${source_filepath}" ]; then
        echo "Symlink source doesn't exist: ${source_filepath}" >&2
        echo "From binding: ${link_def}" >&2
    fi

    link_filepath="$(echo "${link_def}" | cut -d',' -f2)"
    ln -sfn "${source_filepath}" "${link_filepath}"
done
