" -------------------- vim-plug plugins --------------------------
call plug#begin("~/.vim-plug")

" Adds a bunch of vim.lsp configs for the servers here:
" https://github.com/neovim/nvim-lspconfig/blob/master/doc/configs.md
Plug 'neovim/nvim-lspconfig'

Plug 'hrsh7th/cmp-nvim-lsp'
Plug 'hrsh7th/cmp-buffer'
Plug 'hrsh7th/cmp-path'
Plug 'hrsh7th/cmp-cmdline'
Plug 'hrsh7th/nvim-cmp'

" For vsnip users.
Plug 'hrsh7th/cmp-vsnip'
Plug 'hrsh7th/vim-vsnip'

" Both required for jellybeans
Plug 'rktjmp/lush.nvim'
Plug 'metalelf0/jellybeans-nvim'

Plug 'mason-org/mason.nvim'
Plug 'mason-org/mason-lspconfig.nvim'

call plug#end()

" -------------------- nvim-cmp --------------------------
lua require('config.nvim-cmp')

" --------------------- mason --------------------------
lua require('config.mason')

" -------------------- jellybeans --------------------------
colorscheme jellybeans-nvim
