" ========================================================================
"                                 Plugins 
" ========================================================================
source ~/.vim/plugins.vim

" ========================================================================
"                             Neovim-Only Config
" ========================================================================
if has('nvim')
    source ~/.vim/neovim.lua
endif

" ========================================================================
"                          Setting Options
" ========================================================================
" Allow editing Mac crontab with Vim
" Source: http://superuser.com/questions/359580/error-adding-cronjobs-in-mac-os-x-lion
if $VIM_CRONTAB == "true"
    set nobackup
    set nowritebackup
endif

" Open splits on the right and bottom
set splitright
set splitbelow

" Enable syntax highlighting
syntax on

" Ignores whitespace when doing vimdiff
set diffopt+=iwhite

" One of the most important options to activate. Allows you to switch from an
" unsaved buffer without saving it first. Also allows you to keep an undo
" history for multiple files. Vim will complain if you try to quit without
" saving, and swap files will keep you safe if your computer crashes.
set hidden

" Note that not everyone likes working this way (with the hidden option).
" Alternatives include using tabs or split windows instead of re-using the same
" window for multiple buffers, and/or:
" set confirm
" set autowriteall

" Better command-line completion
set wildmenu
set wildignore+=*.so,*.swp,*.zip,*.jar

" Show partial commands in the last line of the screen
set showcmd

" Highlight searches (use <C-L> to temporarily turn off highlighting; see the
" mapping of <C-L> below)
set hlsearch

" Highlight matching parantheses, brackets, braces, etc.
set showmatch

" Modelines have historically been a source of security vulnerabilities. As
" such, it may be a good idea to disable them and use the securemodelines
" script, <http://www.vim.org/scripts/script.php?script_id=1876>.
" set nomodeline

" Set spellcheck for certain files
augroup spellcheck
    autocmd!
    autocmd FileType gitcommit setlocal spell spelllang=en_us,pt_br
    autocmd BufNewFile,BufRead *.markdown setlocal spell spelllang=en_us,pt_br
    autocmd BufNewFile,BufRead *.md setlocal spell spelllang=en_us,pt_br
    autocmd BufNewFile,BufRead *.txt setlocal spell spelllang=en_us,pt_br
augroup END

" Highlight current line
set cursorline

" Use case sensitive search, except when searching
set noignorecase
set incsearch
nnoremap / /\c<Left><Left>
nnoremap ? ?\c<Left><Left>


" Allow backspacing over autoindent, line breaks and start of insert action
set backspace=indent,eol,start

" When opening a new line and no filetype-specific indenting is enabled, keep
" the same indent as the line you're currently on. Useful for READMEs, etc.
set autoindent

" These stop the cursor from being forced to the left when hitting lines
" shorter than the line we started at
set nostartofline

" Display the cursor position on the last line of the screen or in the status
" line of a window
set ruler

" Always display the status line, even if only one window is displayed
" NOTE: This was disabled due to it not playing nicely with Syntastic
set laststatus=2

" Instead of failing a command because of unsaved changes, instead raise a
" dialogue asking if you wish to save changed files.
set confirm

" Use visual bell instead of beeping when doing something wrong
set visualbell

" And reset the terminal code for the visual bell. If visualbell is set, and
" this line is also included, vim will neither flash nor beep. If visualbell
" is unset, this does nothing.
set t_vb=

" Disable use of the mouse for all modes
set mouse=

" Set the command window height to 2 lines, to avoid many cases of having to
" "press <Enter> to continue"
set cmdheight=2

" Display line numbers on the left
set number

" Quickly time out on keycodes, but never time out on mappings
set notimeout ttimeout ttimeoutlen=200

" Lazy redraw, from sensible.vim
set lazyredraw

" Folding options
set foldenable          " Turn on folding
set foldlevelstart=10   " Default show up to 10 levels of folds open on start
set foldnestmax=10      " Don't allow past 10 levels of fold nesting
autocmd FileType *.py setlocal foldmethod=indent   " Automatically fold based on indentation (yay, Python)

" Do not change 'tabstop' from its default value of 8 with this setup.
set shiftwidth=4
set softtabstop=4
set expandtab
autocmd Filetype javascript* setlocal ts=4 sw=4 sts=0
autocmd Filetype yaml setlocal ts=2 sw=2 sts=0

" Indentation settings for using hard tabs for indent. Display tabs as
" two characters wide.
"set shiftwidth=2
"set tabstop=2

" Used for wrapping lines only at words
set wrap
set linebreak

" Try to get Vim to autoreload upon changes
" From https://batsov.com/articles/2025/06/02/how-to-vim-reloading-file-buffers/
set autoread
au FocusGained,BufEnter * :silent! checktime

" Try to fix the issue where Google Drive will re-write the file timestmap to
" their server time while I'm in the middle of editing, and then I get that
" horrible "This file has changed since reading!!!!" error
autocmd BufWritePre * silent! checktime %

" Allow flashing cursor to be seen when matching parenthesis
hi MatchParen ctermfg=white

" Keep cursor centered, except when at the top of the file
set scrolloff=999
autocmd CursorMoved * call AdjustScrolloff()
function! AdjustScrolloff()
  if line('.') <= winheight(0) / 2
    setlocal scrolloff=0
  else
    setlocal scrolloff=999
  endif
endfunction



" ========================================================================
"                                Mappings
" ========================================================================
" Map Y to act like D and C, i.e. to yank until EOL, rather than act as yy,
" which is the default
map Y y$

" Map <C-L> (redraw screen) to also turn off search highlighting until the
" next search
nnoremap <Leader>l :nohl<CR><C-L>

" SYSTEM CLIPBOARD BINDINGS
" Copy current selection to system clipboard
vnoremap + "+y
" Yank the current line
nnoremap ++ "+yy
" Yank the file's contents
nnoremap +% gg0VG"+y''

" Change highlight color on folds to a darker hue
highlight Folded ctermfg=DarkGrey ctermbg=None

" Automatically reload your .vimrc/.gvimrc if something changes
" Doesn't work on all changes (e.g. mappings won't change)
augroup myvimrc
    au!
    au BufWritePost .vimrc,_vimrc,vimrc,.gvimrc,_gvimrc,gvimrc so $MYVIMRC | if has('gui_running') | so $MYGVIMRC | endif
augroup END

" Easy insertion of blank lines
nnoremap ]<Space> o<Esc>
nnoremap [<Space> O<Esc>

" Joins the current line to the previous one with a space
nnoremap <^ ^d0i<BS><Space><Esc>

" Splits everything after the cursor into a new line
nnoremap >v i<Return><Esc>

" Have movement commands operate linewise
nnoremap j gj
nnoremap k gk
nnoremap ^ g^
nnoremap $ g$
vnoremap j gj
vnoremap k gk

" Map <S-j> and <S-k> to PageDown and PageUp respectively
nnoremap J 20jzz
nnoremap K 20kzz
vnoremap J 20jzz
vnoremap K 20kzz

" Easily flip paste mode toggle
nnoremap <Leader>p :set invpaste paste?<CR>

" Screen-centering mappings
nnoremap n nzz
nnoremap N Nzz

" Easy way to echo a line for Bash debugging
nnoremap <Leader>db V:s/"/\\"/g<CR>^iecho "<ESC>$a"<ESC>

" Easy opening of splits
nnoremap <Leader>v :vsp 
nnoremap <Leader>s :sp 
nnoremap <Leader>e :e 

" NOTE: These are cool, but I really shouldn't get used to them for cross-box
" muscle memory... but I love them
" Easy mapping for writing and quitting files
nnoremap <Leader>w :w<CR>
nnoremap <Leader>W :wa<CR>
noremap <Leader>q :q!<CR>
noremap <Leader>Q :qa!<CR>
nnoremap <Leader>x :wq<CR>
nnoremap <Leader>X :wa<CR>:qa<CR>

" Allows easy rendering of Markdown files in Chrome when combined with this
" Markdown viewing Chrome extension:
"  https://chromewebstore.google.com/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk
nnoremap <Leader>c :! open -a 'Google Chrome' "%"<CR><CR>

" This is maybe more valuable as something else
nnoremap <Leader>? :help<CR>

" ---------------------- Markdown file editing-----------------------------
" Very useful shortcut to make a Markdown headers out of given line
nnoremap <Leader>h= "hyy"hpVr=
nnoremap <Leader>h- "hyy"hpVr-
nnoremap <Leader>h# :s/^/### /<CR>:nohl<CR>
" -------------------------------------------------------------------------

nnoremap <Leader>gl :Shell git log --graph --abbrev-commit --decorate --date=relative --format=format:'\%h - (\%ar) \%s [\%an]\%d' --all<CR>

" I often accidentally type :W instead of :w and Vim yells at me. This stops
" that annoying behaviour
command! W w


" ========================================================================
"                            Custom Functions
" ========================================================================
" Nifty command to open the output of a command in a scratch buffer
" Source: http://vim.wikia.com/wiki/Display_output_of_shell_commands_in_new_window
command! -complete=shellcmd -nargs=+ Shell call s:RunShellCommand(<q-args>)
function! s:RunShellCommand(cmdline)
    echo a:cmdline
    let expanded_cmdline = a:cmdline
    for part in split(a:cmdline, ' ')
        if part[0] =~ '\v[%#<]'
            let expanded_part = fnameescape(expand(part))
            let expanded_cmdline = substitute(expanded_cmdline, part, expanded_part, '')
        endif
    endfor
    botright new
    setlocal buftype=nofile bufhidden=wipe nobuflisted noswapfile nowrap
    call setline(1, 'You entered:    ' . a:cmdline)
    call setline(2, 'Expanded Form:  ' .expanded_cmdline)
    call setline(3,substitute(getline(2),'.','=','g'))
    execute '$read !'. expanded_cmdline
    setlocal nomodifiable
    1
endfunction

" Easy JSON prettifier
if !exists(":PrettifyJson")
    :command PrettifyJson %!python3 -m json.tool
endif

function! DoPrettifyXML()
  " save the filetype so we can restore it later
  let l:origft = &ft
  set ft=
  " delete the xml header if it exists. This will
  " permit us to surround the document with fake tags
  " without creating invalid xml.
  1s/<?xml .*?>//e
  " insert fake tags around the entire document.
  " This will permit us to pretty-format excerpts of
  " XML that may contain multiple top-level elements.
  0put ='<PrettyXML>'
  $put ='</PrettyXML>'
  silent %!xmllint --format -
  " xmllint will insert an <?xml?> header. it's easy enough to delete
  " if you don't want it.
  " delete the fake tags
  2d
  $d
  " restore the 'normal' indentation, which is one extra level
  " too deep due to the extra tags we wrapped around the document.
  silent %<
  " back to home
  1
  " restore the filetype
  exe "set ft=" . l:origft
endfunction
command! PrettifyXML call DoPrettifyXML()




" ========================================================================
"                          REMINDERS FOR MYSELF
" ========================================================================
" Merge two blocks of lines: https://stackoverflow.com/questions/10760326/merge-multiple-lines-two-blocks-in-vim
" 1) Select first block of lines you want to merge and yank them to a register
" 2) :let l=split(@THEREGISTER) 
" 3) Select second block of lines
" 4) :'<,'>s/SOMESELECTOR/\=remove(l,0)/

