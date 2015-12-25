# Mieubrisse's Dotfiles Repo

## Commad Line Stuff
* "clip FILE" copies the file to the system clipboard (Mac only)
* "cd NUM.." goes up NUM directories, a la "cd 2.."
* Piping input to "filter" will let the user selectively filter which lines are passed forward. Supports ranges and disjoint sequences, so entering "4,7,1-3" will pass forward (in order) lines 4, 7, 1, 2, and 3
* "ff INPUT" is a shortening of "find -iname '\*INPUT\*'"
* "rgr INPUT" is a shortening of "grep -ir 'INPUT' \*"

## Git Stuff
* ga = add
* gcmm _MESSAGE_ = commit with MESSAGE
* gg _MESSAGE_ = add and commit all modified files (will not add untracked files)
* gs = status
* gb = branch
* gco = checkout
* gcl = git clone
* gl = a colored, succinct graph of the commit history
* gpll = pull
* gf = fetch
* gpsh = git push which will create the remote branch if it doesn't exist
* gprune-local = delete local branches which have been merged in the upstream (useful for deleting branches you're done with)
* gd = diff files not staged for commit
* gdc = diff files staged for commit
* Branch names should autocomplete

## Vim Stuff
* J and K will page down and up respectively
* Pressing + with text highlighted in visual mode will copy it to the system clipboard
* +% will copy the entire file to the system clipboard
* Undo history will be kept even after you close a file
