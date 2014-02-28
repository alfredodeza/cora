``virtual runtime environments for vim``

cora
====
``cora`` solves the problem of being able to carry all your vim configurations
and plugins (a.k.a. runtime files) on a location that is shared or has not been
setup.

All environments are created in a contained way and do not pollute anything on
the system-installed Vim.

Install it::

    pip install cora

Or get it directly with curl from the repository::

    curl -O https://raw.github.com/alfredodeza/cora/master/cora

Note that this is a bit more cumbersome, you will need to make that file
executable and put it somewhere in your path.


Try it::

   cora http://github.com/example/dotfiles myname
