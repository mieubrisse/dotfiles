" -------------------- vim-plug plugins --------------------------
call plug#begin("~/.vim-plug")

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

call plug#end()

" -------------------- nvim-cmp --------------------------
lua require('nvim-cmp')

" -------------------- jellybeans --------------------------
colorscheme jellybeans-nvim
