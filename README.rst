Vim Holmes
==========

With holmes its easy to find specific lines in your project. It's way better
than the built-in `:grep`. Check out these advantages:

#. Results are sorted by relevance.
#. Non-text files are skipped, and so are vcs repositories, minified js and css.
#. Only text snippets are shown for very long lines.
#. You can do LITERAL searches without having to escape symbols.
#. You can search with motions instead of having to type it in.
#. Holmes respects your `smartcase` setting.

Holmes will find what you're looking for!

Installing
----------

Installing vim-holmes is really easy! Just make sure you have `python` in your PATH.

For NeoBundle_ add the following to your `.vimrc`::

    NeoBundle 'dbakker/vim-holmes'

For Vundle_ add the following to your `.vimrc`::

    Bundle 'dbakker/vim-holmes'

For Pathogen_, execute::

    cd ~/.vim/bundle
    git clone https://github.com/dbakker/vim-holmes.git
    vim +Helptags +q

After
-----

Now you can use the Holmes command instead of grep to find anything::

    :Holmes regex
    :HolmesL literal

Add these mappings to your `.vimrc` to use holmes without a lot of typing::

    nmap <leader>hm <Plug>(holmes-motion)
    nmap <leader>hw <Plug>(holmes-inner-word)
    nmap <leader>hs :Holmes<space>
    nmap <leader>hl :HolmesL<space>

Check out `:help holmes` to find out what more you can do!

License
=======

Copyright (c) Daan Bakker. Distributed under the same terms as Vim itself. See `:help license`.

.. _Vundle: https://github.com/gmarik/vundle
.. _Pathogen: https://github.com/tpope/vim-pathogen
.. _NeoBundle: https://github.com/Shougo/neobundle.vim
