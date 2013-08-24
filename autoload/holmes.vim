if &cp || exists('autoloaded_holmes') || !executable('python')
  finish
endif
let autoloaded_holmes = 1

if !exists('s:holmes_exe')
  let paths = substitute(escape(&runtimepath, ' '), '\(,\|$\)', '/**\1', 'g')
  let s:holmes_exe = "python '".fnamemodify(findfile('holmes.py', paths), ':p')."'"

  if &shell == '/bin/zsh'
    let s:holmes_exe = 'noglob '.s:holmes_exe
  endif
endif

if !exists("g:holmes_apply_qmappings")
  let g:holmes_apply_qmappings = !exists("g:holmes_qhandler")
endif

if !exists("g:holmes_apply_lmappings")
  let g:holmes_apply_lmappings = !exists("g:holmes_lhandler")
endif

if !exists("g:holmes_qhandler")
  let g:holmes_qhandler="botright copen"
endif

if !exists("g:holmes_lhandler")
  let g:holmes_lhandler="botright lopen"
endif

fun! s:encode(arg)
  return a:arg=~#'^\w\+$' ? a:arg : "'".substitute(a:arg, "'", "'\"'\"'", 'g')."'"
endf

fun! holmes#search(cmd, args)
  redraw
  echo "Searching ..."

  let args = ' --source '.s:encode(expand('%'))
  if exists('b:holmes_exclude')
    let args .= ' --exclude '.s:encode(b:holmes_exclude)
  elseif exists('g:holmes_exclude')
      let args .= ' --exclude '.s:encode(g:holmes_exclude)
  endif
  if exists('b:holmes_low_priority')
    let args .= ' --low-priority '.s:encode(b:holmes_low_priority)
  elseif exists('g:holmes_low_priority')
    let args .= ' --low-priority '.s:encode(g:holmes_low_priority)
  endif
  if exists('g:holmes_smartcase')
    let args .= g:holmes_smartcase>0 ? ' --smart-case' : ''
  elseif &smartcase
    let args .= ' --smart-case'
  endif
  if exists('b:holmes_extra_args')
    let args .= ' '.b:holmes_extra_args
  elseif exists('g:holmes_extra_args')
    let args .= ' '.g:holmes_extra_args
  endif

  let args .= ' '.(len(a:args) > 0 ? a:args : expand('<cword>'))

  let grepprg_bak=&grepprg
  let grepformat_bak=&grepformat
  try
    let &grepprg=s:holmes_exe
    let &grepformat="%f:%l:%c:%m"
    silent execute a:cmd args
  finally
    let &grepprg=grepprg_bak
    let &grepformat=grepformat_bak
  endtry

  if a:cmd =~# '^l'
    exe g:holmes_lhandler
    let l:apply_mappings = g:holmes_apply_lmappings
  else
    exe g:holmes_qhandler
    let l:apply_mappings = g:holmes_apply_qmappings
  endif

  if l:apply_mappings
    exec "nnoremap <silent> <buffer> q :ccl<CR>"
    exec "nnoremap <silent> <buffer> t <C-W><CR><C-W>T"
    exec "nnoremap <silent> <buffer> T <C-W><CR><C-W>TgT<C-W><C-W>"
    exec "nnoremap <silent> <buffer> o <CR>"
    exec "nnoremap <silent> <buffer> go <CR><C-W><C-W>"
    exec "nnoremap <silent> <buffer> h <C-W><CR><C-W>K"
    exec "nnoremap <silent> <buffer> H <C-W><CR><C-W>K<C-W>b"
    exec "nnoremap <silent> <buffer> v <C-W><CR><C-W>H<C-W>b<C-W>J<C-W>t"
    exec "nnoremap <silent> <buffer> gv <C-W><CR><C-W>H<C-W>b<C-W>J"
  endif

  " If highlighting is on, highlight the search keyword.
  if exists("g:holmeshighlight")
    let @/=a:args
    set hlsearch
  end

  redraw!
endf

fun! holmes#literal(cmd, args, ...)
  let options = '--literal ' . (a:0 > 0 ? a:1.' ' : '')
  let args = s:encode(len(a:args) > 0 ? a:args : expand('<cword>'))
  call holmes#search(a:cmd, options.'-- '.args)
endf

fun! holmes#fromsearch(cmd, args)
  let search = getreg('/')
  " translate vim regular expression to perl regular expression.
  let search = substitute(search,'\(\\<\|\\>\)','\\b','g')
  call holmes#search(a:cmd, '"' .  search .'" '. a:args)
endf

fun! holmes#motion(type) abort
  let reg_save = @@

  if a:type ==# 'v'
    sil exe "normal! `<" . a:type . "`>y"
  elseif a:type ==# 'char'
    sil exe "normal! `[v`]y"
  endif

  call holmes#literal("grep!", @@)
  let @@ = reg_save
endf
