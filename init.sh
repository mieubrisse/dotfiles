# Little script to initialize all my dotfiles and things on a new box

set -euo pipefail
script_dirpath="$(cd "$(dirname "${0}")" && pwd)"

# Create various needed directories
ipython_dirpath="${HOME}/.ipython/profile_default"
mkdir -p "${ipython_dirpath}"
keybindings_dirpath="${HOME}/Library/KeyBindings"
mkdir -p "${keybindings_dirpath}"

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
  "${script_dirpath}/keybindings/DefaultKeyBinding.dict,${keybindings_dirpath}/DefaultKeyBinding.dict"
	"${script_dirpath}/intellij-idea/ideavimrc,${HOME}/.ideavimrc"
  "${script_dirpath}/fd/fdignore,${HOME}/.fdignore"
)

for link_def in "${symlink_arr[@]}"; do
	source_filepath="$(echo "${link_def}" | cut -d',' -f1)"
	link_filepath="$(echo "${link_def}" | cut -d',' -f2)"
	ln -sfn "${source_filepath}" "${link_filepath}"
done
