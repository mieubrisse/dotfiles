Neovim Config
=============
This Neovim directory is also the same that gets placed into `.vim`.

The goal is to maintain compatibility with both Vim and Neovim.


```
init.vim                Entrypoint for everything
autoload/               Automatically loaded by both Vim and Neovim
    plug.vim            Set up vim-plug
common-plugins.vim      Plugins for both Neovim & Vim
vim-only-plugins.vim    Plugins for Vim only
neovim-plugins.lua      Plugins for Neovim only
lua/                    Neovim Lua configuration modules
    nvim-cmp.vim        Set up nvim-cmp
```

