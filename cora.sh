#!/bin/sh

#
# A shell included with this package that will make it easier to alter the
# $PATH environment variable to point to a virtual runtime environment previously
# created.
#
# As opposed to manually having to call ``export`` with the location
#

zdotdir=''
bashrc=''

function vre_path {
    DIR="$HOME/.cora/$1"
    if [ -d "$DIR" ]; then
        echo "$DIR"
    fi
}

function shell_flags {
    if [ -n "$BASH" ]
    then
        echo "-i --rcfile $bashrc"
    elif [ -n "$ZSH_VERSION" ]
    then
        echo "-i"
    fi
}

function shell_cmd {
    if [ -n "$BASH" ]
    then
        echo "$SHELL "
    elif [ -n "$ZSH_VERSION" ]
    then
        echo "ZDOTDIR=$zdotdir $SHELL "
    fi
}

vre_bin="$(vre_path)$1/runtime/bin"

#if [ ! -e "$vre_bin" ]; then
#    echo "Did not find virtual runtime directory: $vre_bin"
#else
#    export VIM=$vre_bin/vim
#    exec $SHELL
#fi

if [ "$#" = 1 ]; then
    export CORA_USERNAME="$1"
fi
if [ "$#" = 2 ]; then
    export CORA_URL="$1"
    export CORA_USERNAME="$2"
fi
