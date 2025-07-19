call plug#begin("~/.vim-plug")

" Seems like jellybeans has gone out of development
Plug 'nanotech/jellybeans.vim'

call plug#end()

" -------------------------- jellybeans --------------------------------
colorscheme jellybeans
" let g:jellybeans_background_color_256 = "000000"
let g:jellybeans_overrides = {
\    'background': { 'guibg': '000000' },
\}
