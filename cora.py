#!/usr/bin/env python

import sys
import os
import subprocess

coravimrc_contents = """
set nocompatible

" prune ~/.vim out of the mix so that we can set our own
let &runtimepath = printf('%s/vimfiles,%s,%s/vimfiles/after', $VIM, $VIMRUNTIME, $VIM)

" what is the name of the directory containing this file?
let s:portable = expand('<sfile>:p:h')

" add the s:portable directory to 'runtimepath' so that all other configs
" become available
let &runtimepath = printf('%s,%s,%s/after', s:portable, &runtimepath, s:portable)

" finally, now that all things are set, source the user's .vimrc file
source {runtime_vimrc_path}
"""

vim_contents = """#!/bin/sh
{vim_path} -Nu {coravimrc} $*
"""

cora_path = os.path.expanduser('~/.cora')

def which_vim():
    executable = 'vim'
    locations = [
        '/usr/local/bin',
        '/bin',
        '/usr/bin',
        '/usr/local/sbin',
        '/usr/sbin',
        '/sbin',
    ]

    for location in locations:
        executable_path = os.path.join(location, executable)
        if os.path.exists(executable_path):
            return executable_path
    raise SystemExit('could not find vim executable')


def run(cmd, **kw):
    stop_on_nonzero = kw.pop('stop_on_nonzero', True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        **kw
    )

    if process.stderr:
        while True:
            err = process.stderr.readline()
            if err == '' and process.poll() is not None:
                break
            if err != '':
                sys.stderr.write(err)
                sys.stderr.flush()
    if process.stdout:
        while True:
            out = process.stdout.readline()
            if out == '' and process.poll() is not None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()


def looks_like_url(argument):
    if argument.startswith(('http', 'git', 'ssh')):
        return True
    return False


def ensure_cora_dir():
    if not os.path.exists(cora_path):
        os.mkdir(cora_path)


def find_vimrc(starting_path):
    for root, dirs, files in os.walk(starting_path):
        for name in files:
            if name == '.vimrc':
                return os.path.abspath(os.path.join(root, name))
    raise SystemExit('booo we could not find a .vimrc file :(')


def find_vim(starting_path):
    for root, dirs, files in os.walk(starting_path):
        for name in dirs:
            if name == '.vim':
                return os.path.abspath(os.path.join(root, name))
    raise SystemExit('booo we could not find a .vim directory :(')



def make_virtualenv(repo_path):
    print 'making virtualenv from %s' % repo_path
    runtime_path = os.path.join(os.path.dirname(repo_path), 'runtime')

    # this would mean nothing was crawled and set, so make it happen
    if not os.path.exists(runtime_path):
        os.mkdir(runtime_path)

        vimrc = find_vimrc(repo_path)
        vim = find_vim(repo_path)
        vim_executable = which_vim()

        bin_dir = os.path.join(runtime_path, 'bin')
        virtual_vim_executable = os.path.join(bin_dir, 'vim')
        vim_destination = os.path.join(runtime_path, '.vim')
        coravimrc = os.path.join(vim_destination, 'coravimrc')
        os.mkdir(bin_dir)
        import shutil
        shutil.copytree(vim, os.path.join(runtime_path, '.vim'))
        shutil.copyfile(vimrc, os.path.join(vim_destination, '.vimrc'))

        with open(coravimrc, 'w') as coravimrc_file:
            coravimrc_file.write(coravimrc_contents.format(
                runtime_vimrc_path=os.path.join(vim_destination, '.vimrc'))
            )

        with open(virtual_vim_executable, 'w') as vim_file:
            vim_file.write(
                vim_contents.format(
                    vim_path=vim_executable,
                    coravimrc=coravimrc
                )
            )

        os.chmod(virtual_vim_executable, 0755)


    # otherwise we are just returning here, so we are good to go.
    # set the PATH environment variable and be done.
    print 'vim virtual runtime set'
    print 'before using it you will need to alter $PATH'
    print 'export PATH=%s:$PATH' % os.path.join(runtime_path, 'bin')




def main():
    if len(sys.argv) < 2:
        print 'you le suck, need to specify an HTTP repo and a name or just a name'
        print 'like:'
        print '    cora http://github.com/username/dotfiles alfredo'
        print 'or:'
        print '    cora alfredo'
        raise SystemExit()

    if len(sys.argv) == 2 and sys.argv[-1] in os.path.listdir(cora_path):
        clone_destination = os.path.join((os.path.join(cora_path, sys.argv[-1])), 'repo')
        return make_virtualenv(clone_destination)
    if len(sys.argv) < 3:
        print 'you le suck, need to specify an HTTP repo and a name'
        print 'like: cora http://github.com/username/dotfiles alfredo'

    url, username = sys.argv[1:]
    if not looks_like_url(url):
        raise SystemExit('first argument does not look like an url: %s' % url)

    ensure_cora_dir()
    clone_destination = os.path.join(os.path.join(cora_path, username), 'repo')
    run(['git', 'clone', url, clone_destination])
    os.chdir(clone_destination)
    run(['git', 'submodule', 'update', '--init', '--recursive'])

    return make_virtualenv(clone_destination)


if __name__ == '__main__':
    main()
