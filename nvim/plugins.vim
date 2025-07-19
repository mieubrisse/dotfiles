" ----------------------------- Vundle -----------------------------------
" Set 'nocompatible' to ward off unexpected things that your distro might
" have made, as well as sanely reset options when re-sourcing .vimrc
" This is also required for Vundle
set nocompatible

" Required for Vundle install
filetype off

" ---------------------------- vim-polyglot ------------------------------
" vim-polyglot wants you to set this BEFORE loading the plugin
" Because our plugins get loaded below, we set this here
" We disable markdown polyglot on markdown and csv, because it's weird
let g:polyglot_disabled = ['markdown', 'csv']
let g:csv_no_conceal = 1

" ------------------------- Vim-Plug Plugins ------------------------------
" NOTES:
" - :PlugInstall is required after adding a plugin here!!!!
" - :PlugClean will remove old plugins

" Helper for conditionally activating plugins
" From: https://github.com/junegunn/vim-plug/wiki/tips#conditional-activation
function! Cond(cond, ...)
  let opts = get(a:000, 0, {})
  return a:cond ? opts : extend(opts, { 'on': [], 'for': [] })
endfunction

call plug#begin("~/.vim-plug")

" if has('nvim')
"     Plug 'neovim/nvim-lspconfig'
"     Plug 'hrsh7th/cmp-nvim-lsp'
"     Plug 'hrsh7th/cmp-buffer'
"     Plug 'hrsh7th/cmp-path'
"     Plug 'hrsh7th/cmp-cmdline'
"     Plug 'hrsh7th/nvim-cmp'
" 
"     " For vsnip users.
"     Plug 'hrsh7th/cmp-vsnip'
"     Plug 'hrsh7th/vim-vsnip'
" endif


Plug 'vim-scripts/groovy.vim'
Plug 'tfnico/vim-gradle'
Plug 'uarun/vim-protobuf'
" Plug 'kien/ctrlp.vim'
" Plug 'scrooloose/nerdtree'
Plug 'tomtom/tcomment_vim'
" Plug 'davidhalter/jedi-vim'
Plug 'leafgarland/typescript-vim'

" Both of these are required for plasticboy's Markdown syntax
Plug 'godlygeek/tabular'
Plug 'plasticboy/vim-markdown'

" All the Vim YAML plugins are miserable...
" Plug 'avakhov/vim-yaml'
" Plug 'chase/vim-ansible-yaml'

" Plug 'tomtom/tlib_vim'
" Plug 'MarcWeber/vim-addon-mw-utils'
" Plug 'kchmck/vim-coffee-script'
" Plug 'easymotion/vim-easymotion'
" Plug 'pangloss/vim-javascript'
Plug 'sheerun/vim-polyglot'
Plug 'elzr/vim-json'
Plug 'groenewege/vim-less'
Plug 'kshenoy/vim-signature'
" Plug 'derekwyatt/vim-scala'
" Plug 'garbas/vim-snipmate'
" Plug 'SirVer/ultisnips'
" Plug 'honza/vim-snippets'
" Plug 'tristen/vim-sparkup'
" Plug 'tpope/vim-surround'
" Plug 'sukima/xmledit'
Plug 'airblade/vim-gitgutter'
" Plug 'mustache/vim-mustache-handlebars'
" Plug 'fatih/vim-go'
Plug 'vim-airline/vim-airline'
" Plug 'tpope/vim-fugitive'
" Plug 'gregsexton/gitv'
" Plug 'kablamo/vim-git-log'
Plug 'maxbrunsfeld/vim-yankstack'

" Syntax highlighting for CSV, since polyglot's is bad
Plug 'mechatroner/rainbow_csv'


" Neovim-specific plugins
if has('nvim')
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
    " Plug 'rktjmp/lush.nvim'
    " Plug 'metalelf0/jellybeans-nvim'

    Plug 'mason-org/mason.nvim'
    Plug 'mason-org/mason-lspconfig.nvim'

    " Plug 'folke/tokyonight.nvim'

    " Plug 'rebelot/kanagawa.nvim'

    Plug 'scottmckendry/cyberdream.nvim'
else
    " Seems like jellybeans has gone out of development
    Plug 'nanotech/jellybeans.vim'
endif

" All Plug calls must be executed before this
call plug#end()
" ---------------------------- End Vim-Plug Plugins ------------------------


" Attempt to determine the type of a file based on its name and possibly its
" contents. Use this to allow intelligent auto-indenting for each filetype,
" and for plugins that are filetype specific.
" Required to tun back on for Vundle stuff to work
filetype plugin indent on

" ---------------------- Plasticboy Markdown Plugin ----------------------
" This fancy stuff doens't work as well as I'd like so I get rid of it
let g:vim_markdown_auto_insert_bullets = 0
let g:vim_markdown_new_list_item_indent = 0
let g:vim_markdown_folding_disabled = 1
let g:vim_markdown_conceal = 0
let g:vim_markdown_strikethrough = 1


" ---------------------------- yankstack ----------------------------------
let g:yankstack_map_keys = 0
nmap <C-p> <Plug>yankstack_substitute_older_paste
nmap <C-n> <Plug>yankstack_substitute_newer_paste

" ------------------------------ Ansible YAML ----------------------------
" Vim's built-in YAML doesn't handle indentation well, so we need to use the only
" YAML plugin that actually does it right
" Why do all the YAML plugins suck... :(
" au BufRead,BufNewFile *.yml set filetype=ansible
" au BufRead,BufNewFile *.yaml set filetype=ansible
autocmd FileType *.yml setlocal noautoindent
autocmd FileType *.yaml setlocal noautoindent

" ---------------------------- Starlark ----------------------------------
" The only Vim Starlark plugin uses weird coloring, so we set the syntax to
" Python
autocmd FileType *.star setlocal filetype=python

" ---------------------------- Jedi Vim ----------------------------------
let g:jedi#documentation_command = ""
let g:jedi#popup_select_first = 1

" This turns off the annoying 'insert the autocomplete match if there's only one'
" behavior
if v:version >= 705 || (v:version == 704 && has('patch775'))
   set completeopt=menuone,longest,preview,noinsert
endif

" ----------------------------- Airline ----------------------------------
let g:airline_left_sep=''
let g:airline_right_sep=''

" I really only care about percentage through file, so only show me that
let g:airline_section_z = airline#section#create(['%3p%%'])

" ---------------------------- Gitgutter ---------------------------------
nnoremap <Leader>ha :GitGutterStageHunk<CR>


if has('nvim')
    " -------------------- nvim-cmp --------------------------
    lua require('config.nvim-cmp')

    " --------------------- mason --------------------------
    lua require('config.mason')

    " -------------------- jellybeans-nvim --------------------------
    " lua require('config.jellybeans')

    " -------------------- kanagawa --------------------------
    lua require('config.theme')
else
    " -------------------------- jellybeans.vim --------------------------------
    colorscheme jellybeans
    " let g:jellybeans_background_color_256 = "000000"
    let g:jellybeans_overrides = {
    \    'background': { 'guibg': '000000' },
    \}
endif
