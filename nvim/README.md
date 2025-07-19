Neovim Config
=============
This Neovim directory is also the same that gets placed into `.vim`.

The goal is to maintain compatibility with both Vim and Neovim.


```
init.vim                Entrypoint for everything
common-plugins.vim      Vim-plug plugins (common to both Neovim and regular Vim)
autoload/               Automatically loaded by both Vim and Neovim
    plug.vim            Set up vim-plug
neovim-plugins.lua      Activates Neovim-only plugins
lua/                    Neovim Lua configuration modules
    config/             A directory for 
        lazy.vim        Set up lazy.nvim
        nvim-cmp.vim     Set up 
    plugins/            Directory to house lazy.nvim's plugins
        thing1.lua      
        ...
```

