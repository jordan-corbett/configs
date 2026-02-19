call plug#begin()
Plug 'tpope/vim-fugitive'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'preservim/nerdtree'
Plug 'mattn/emmet-vim'
Plug 'tpope/vim-commentary'
Plug 'dmerejkowsky/vim-ale'
Plug 'gkjgh/cobalt'
Plug 'Rigellute/rigel'
Plug 'azabiong/vim-highlighter'
Plug 'mhinz/vim-signify', { 'tag': 'legacy' }
Plug 'python-mode/python-mode', { 'for': 'python', 'branch': 'develop' } " pip install setuptools
Plug 'ycm-core/youcompleteme'
call plug#end()

set encoding=utf-8

set tabstop=4
set shiftwidth=4
set expandtab
set nu

autocmd FileType javascript setlocal shiftwidth=2 tabstop=2
autocmd FileType typescript setlocal shiftwidth=2 tabstop=2
filetype plugin on

if (has('termguicolors'))
    set termguicolors
endif

syntax enable
colorscheme cobalt

let g:airline_powerline_fonts = 1
let g:rigel_airline = 1
let g:airline_theme = 'rigel'

let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#formatter = 'unique_tail_improved'

" pymode
let g:pymode_indent = 1
let g:pymode_virtualenv = 1

" aliases
command NT NERDTree

silent! helptags ALL
