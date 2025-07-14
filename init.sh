# Idempotently symlinks everything into the correct location

set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"

ipython_dirpath="${HOME}/.ipython/profile_default"
claude_dirpath="${HOME}/.claude"
karabiner_config_dirpath="${HOME}/.config/karabiner"

# Create various needed directories
dirpaths_to_create=(
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
	"${script_dirpath}/git/gitignore,${HOME}/.gitignore"
	"${script_dirpath}/git/gitconfig,${HOME}/.gitconfig"
	"${script_dirpath}/vim,${HOME}/.vim"
	"${script_dirpath}/bash/utils,${HOME}/.bash_utils"
	"${script_dirpath}/bash/editrc,${HOME}/.editrc"
	"${script_dirpath}/tmux/tmux.conf,${HOME}/.tmux.conf"
	"${HOME}/.bashrc,${HOME}/.bash_profile"
	"${HOME}/.vim/vimrc,${HOME}/.vimrc"
  "${script_dirpath}/ipython/ipython_config.py,${ipython_dirpath}/ipython_config.py"
	"${script_dirpath}/intellij-idea/ideavimrc,${HOME}/.ideavimrc"
  "${script_dirpath}/fd/fdignore,${HOME}/.fdignore"
  "${HOME}/Google Drive/My Drive,${HOME}/gdrive" # Google Drive
  "${script_dirpath}/karabiner,${karabiner_config_dirpath}" # Karabiner config
  "${script_dirpath}/claude/CLAUDE.md,${claude_dirpath}/CLAUDE.md"
)

for link_def in "${symlink_arr[@]}"; do
	source_filepath="$(echo "${link_def}" | cut -d',' -f1)"
	link_filepath="$(echo "${link_def}" | cut -d',' -f2)"
	ln -sfn "${source_filepath}" "${link_filepath}"
done
