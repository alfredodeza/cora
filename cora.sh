#!/bin/sh

#
# A shell included with this package that will make it easier to alter the
# $PATH environment variable to point to a virtual runtime environment previously
# created.
#
# As opposed to manually having to call ``export`` with the location
#

function vre_path {
    DIR="$HOME/.cora/$CORA_USERNAME"
    if [ -d "$DIR" ]; then
        echo "$DIR"
    fi
}

function shell_flags {
    if [ -n "$ZSH_VERSION" ]
    then
        echo "-i"

    elif [ -n "$BASH_VERSION" ]
    then
        echo "-i --rcfile $(bashrc)"
    fi
}


function shell_cmd {
    # Attempt to get the right command to call for exec. It is actually tricky
    # to determine if we are BASH or ZSH because if we are on ZSH and are
    # executing the current script via /bin/sh which can be aliased to BASH
    # then we will fail to correctly set the right commands.
    #
    # Finally, we cannot fully rely on $SHELL because the actual path for that
    # shell might be a bit different so we need to call `which` on it to get
    # the right PATH to the executable.
    #
    if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]
    then
        executable=`which zsh`
        export ZDOTDIR="$(zdotdir)"
        echo "$executable -i"
    elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]
    then
        executable=`which bash`
        echo "$executable $(shell_flags)"
    fi
}


function success {
    if [ -e "$(vre_path)/.done" ]; then
        echo 1
    fi
}


function zdotdir {
    echo "$(vre_path)/rc"
}


function bashrc {
    echo "$(vre_path)/rc/.bashrc"
}


if [ "$#" = 1 ]; then
    export CORA_USERNAME="$1"
fi

if [ "$#" = 2 ]; then
    export CORA_URL="$1"
    export CORA_USERNAME="$2"
fi

vre_bin="$(vre_path)/bin"

if [ -n "$(success)" ]; then

    if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]
    then
        executable=`which zsh`
        export ZDOTDIR="$(zdotdir)"
        exec $executable -i
    elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]
    then
        executable=`which bash`
        exec $executable $(shell_flags)
    fi

fi
