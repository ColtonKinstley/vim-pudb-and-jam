" File: pudb.vim
" Author: Christophe Simonis, Michael van der Kamp
" Description: Manage pudb breakpoints directly from vim


if exists('g:loaded_pudb_plugin') || &compatible
    finish
endif
let g:loaded_pudb_plugin = 1

if !has('pythonx')
    echoerr 'vim-pudb requires vim compiled with +python and/or +python3'
    finish
endif

if !has('signs')
    echoerr 'vim-pudb requires vim compiled with +signs'
    finish
endif


""
" Load options and set defaults
""
let g:pudb_sign       = get(g:, 'pudb_sign',       'B>')
let g:pudb_highlight  = get(g:, 'pudb_highlight',  'error')
let g:pudb_priority   = get(g:, 'pudb_priority',   100)
let g:pudb_sign_group = get(g:, 'pudb_sign_group', 'pudb_sign_group')

call sign_define('PudbBreakPoint', {
            \   'text':   g:pudb_sign,
            \   'texthl': g:pudb_highlight
            \ })


""
" Everything is defined in a python module on the runtimepath!
""
pyx import pudb_and_jam

""
" Define ex commands for all the above functions so they are user-accessible.
""
command! PudbClearAll pyx pudb_and_jam.clearAll()
command! PudbEdit     pyx pudb_and_jam.edit()
command! PudbList     pyx pudb_and_jam.list()
command! PudbLocList  pyx pudb_and_jam.locationList()
command! PudbQfList   pyx pudb_and_jam.quickfixList()
command! PudbToggle   pyx pudb_and_jam.toggle()
command! PudbUpdate   pyx pudb_and_jam.update()
command! -nargs=1 -complete=command PudbPopulateList
            \ pyx pudb_and_jam.populateList("<args>")


""
" If we were loaded lazily, update immediately.
""
if &filetype ==? 'python'
    pyx pudb_and_jam.update()
endif


augroup pudb
    " Also update when the file is first read.
    autocmd BufReadPost *.py PudbUpdate

    " Force a linecache update after writes so the breakpoints can be parsed
    " correctly.
    autocmd BufWritePost *.py pyx pudb_and_jam.clearLineCache()
augroup end
