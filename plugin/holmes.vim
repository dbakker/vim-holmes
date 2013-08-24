if &cp || exists('loaded_holmes') || !executable('python')
    finish
endif
let loaded_holmes = 100

" Vim plugin code adapted from the Ack.vim plugin

command! -bang -nargs=* -complete=file Holmes call holmes#search('grep<bang>', <q-args>)
command! -bang -nargs=* HolmesL call holmes#literal('grep<bang>', <q-args>)
command! -bang -nargs=* -complete=file HolmesAdd call holmes#search('grepadd<bang>', <q-args>)
command! -bang -nargs=* -complete=file HolmesFromSearch call holmes#fromsearch('grep<bang>', <q-args>)
command! -bang -nargs=* -complete=file LHolmes call holmes#search('lgrep<bang>', <q-args>)
command! -bang -nargs=* -complete=file LHolmesAdd call holmes#search('lgrepadd<bang>', <q-args>)

nnoremap <silent> <Plug>(holmes-motion) :set opfunc=holmes#motion<CR>g@
xnoremap <silent> <Plug>(holmes-motion) :<C-U>call holmes#motion(visualmode())<CR>

nnoremap <silent> <Plug>(holmes-inner-word) :<C-U>call holmes#literal('grep!','','--word-regexp')<CR>
xmap <silent> <Plug>(holmes-inner-word) <Plug>(holmes-motion)
