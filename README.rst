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

The second argument is required when passing a url and that should be the
username to identify this new vim virtual runtime files (a.k.a. your
nick/username).


requirements
------------
This tool requires ``git`` installed and that you have your dotfiles (or your
``.vimrc`` and ``.vim``) published in a git repository.

The alternative is to have a copy of a directory with both your ``.vimrc`` file and
``.vim`` directory and point ``cora`` to it instead of a url.

You **must** have a ``.vim`` or ``vim`` directory in your dotfiles and you
**must** have a ``vimrc`` or ``.vimrc`` file too. ``cora`` will search for
these and copy them over to create the virtual runtime environment.


What does it do with a url
--------------------------
Running the ``cora`` will git clone the url (first argument) and will create
a hidden directory in ``$HOME/.cora`` if it doesn't exist.

The cloned repository will got into ``$HOME/.cora/nickname/repo``. It is
**required** to pass in the ``nickname`` argument.

Once the repository is cloned the tool will run an update on the git submodules
to ensure that all repositories used as plugins are up to date with: ``git
submodule update --init --recursive``.

What does it do with a directory
--------------------------------
If you have a directory with your ``.vimrc`` and ``.vim`` directory then all it
does is copy those to ``$HOME/.cora/nickname/repo``.

Again, you need to pass in a nickname as a second argument so that cora knows
where to put the runtime files::

    cora /path/to/my/dotfiles nickname


existing environments
---------------------
If the environment was already created then cora will simply need to know the
nickname that was used to created. For a nickname ``alfredo`` this would be::

To set the ``$PATH`` manually::

    cora alfredo

Or do it with the cora helper::

    coras alfredo

virtual runtime environments
----------------------------
These consist of a few things, and it is not very interesting unless you need
to know ``cora`` internals. The ``.vim`` directory and ``.vimrc`` file get
copied here.

A ``coravimrc`` file is created that mangles the variables that Vim uses to
find and detect runtime files to point to that location and that in turn will
source the ``.vimrc`` from the user's dotfiles copied previously.

It finally consists of a ``bin/`` directory that has a ``vim`` executable that
points to that ``coravimrc`` file
