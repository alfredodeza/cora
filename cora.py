#!/usr/bin/env python

import sys
import os
import subprocess

coravimrc_contents = """
set nocompatible

" prune ~/.vim out of the mix so that we can set our own
let &runtimepath = printf('%s/vimfiles,%s,%s/vimfiles/after', \$VIM, \$VIMRUNTIME, \$VIM)

" what is the name of the directory containing this file?
let s:portable = expand('<sfile>:p:h')

" add the s:portable directory to "runtimepath" so that all other configs
" become available
let &runtimepath = printf('%s,%s,%s/after', s:portable, &runtimepath, s:portable)

" finally, now that all things are set, source the user's .vimrc file
source {runtime_vimrc_path}
"""

rc_contents = """
# Sources the user"s RC file for the current \$SHELL
source {rc_path}

# After sourcing we redo the \$PATH setting our vim first
export PATH={bin_dir}:\$PATH
"""


vim_contents = """#!/bin/sh
{vim_path} -Nu {coravimrc} \$*
"""

cora_path = os.path.expanduser("~/.cora")


def colorize(msg, color):
    available = dict(
            blue = '\033[94m',
            green = '\033[92m',
            yellow = '\033[93m',
            red = '\033[91m',
            bold = '\033[1m',
            ends = '\033[0m'
        )
    return "%s%s%s" % (available[color], msg, available['ends'])


def warning(msg):
    sys.stdout.write("%s %s\n" % (colorize('>>>', 'yellow'), msg))


def debug(msg):
    sys.stdout.write("%s %s\n" % (colorize('>>>', 'blue'), msg))


def info(msg):
    sys.stdout.write("%s %s\n" % (colorize('>>>', 'bold'), msg))


def error(msg):
    sys.stdout.write("%s %s\n" % (colorize('>>>', 'red'), msg))


def which_vim():
    executable = "vim"
    locations = [
        "/usr/local/bin",
        "/bin",
        "/usr/bin",
        "/usr/local/sbin",
        "/usr/sbin",
        "/sbin",
    ]

    for location in locations:
        executable_path = os.path.join(location, executable)
        if os.path.exists(executable_path):
            return executable_path
    raise SystemExit("could not find vim executable")


def run(cmd, **kw):
    info(' '.join(cmd))

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        **kw
    )

    if process.stderr or process.stout:
        while True:
            err = process.stderr.readline()
            if err == "" and process.poll() is not None:
                break
            if err != "":
                warning(err.strip('\n'))
                sys.stderr.flush()

            out = process.stdout.readline()
            if out == "" and process.poll() is not None:
                break
            if out != "":
                debug(out.strip('\n'))
                sys.stdout.flush()


def looks_like_url(argument):
    if argument.startswith(("http", "git", "ssh")):
        return True
    return False


def ensure_dir(_path):
    if not os.path.exists(_path):
        os.mkdir(_path)


def find_vimrc(starting_path):
    for root, dirs, files in os.walk(starting_path):
        for name in files:
            if name == ".vimrc" or name == "vimrc":
                return os.path.abspath(os.path.join(root, name))
    raise SystemExit("booo we could not find a .vimrc file :(")


def find_vim(starting_path):
    for root, dirs, files in os.walk(starting_path):
        for name in dirs:
            if name == ".vim" or name == "vim":
                return os.path.abspath(os.path.join(root, name))
    raise SystemExit("booo we could not find a .vim directory :(")


def make_virtualenv(repo_path):
    info("making virtualenv from %s" % repo_path)
    base_path = os.path.dirname(repo_path)
    runtime_path = os.path.join(os.path.dirname(repo_path), "runtime")
    rc_path = os.path.join(os.path.dirname(repo_path), "rc")
    bin_dir = os.path.join(base_path, "bin")
    virtual_vim_executable = os.path.join(bin_dir, "vim")
    vim_destination = os.path.join(runtime_path, ".vim")
    vimrc_destination = os.path.join(vim_destination, ".vimrc")
    coravimrc = os.path.join(vim_destination, "coravimrc")

    # this would mean nothing was crawled and set, so make it happen
    if not os.path.exists(runtime_path):
        os.mkdir(runtime_path)
        os.mkdir(rc_path)

        vimrc = find_vimrc(repo_path)
        vim = find_vim(repo_path)
        vim_executable = which_vim()

        os.mkdir(bin_dir)

        debug("symlinking: %s %s" % (vim, vim_destination))
        os.symlink(vim, vim_destination)
        debug("symlinking: %s %s" % (vimrc, vimrc_destination))
        os.symlink(vimrc, vimrc_destination)

        # Ungh python 2.4
        coravimrc_file = open(coravimrc, "w")
        coravimrc_file.write(coravimrc_contents.format(
            runtime_vimrc_path=vimrc_destination)
        )
        coravimrc_file.close()
        debug("created coravimrc at %s" % coravimrc)

        vim_file = open(virtual_vim_executable, "w")
        vim_file.write(
            vim_contents.format(
                vim_path=vim_executable,
                coravimrc=coravimrc
            )
        )
        vim_file.close()
        debug("created vim executable: %s" % virtual_vim_executable)

        os.chmod(virtual_vim_executable, 0755)

    # otherwise we are just returning here, so we are good to go.
    # set the PATH environment variable and be done.
    info("vim virtual runtime set! Happy vimming...")
    new_path = "export PATH=%s:\$PATH\n" % bin_dir
    write_rc_file(rc_path, new_path, vim_destination)

    with open(os.path.join(base_path, '.done'), 'w') as done_file:
            done_file.write(new_path)


def write_rc_file(rc_path, new_path, new_vim):
    zshrc = open(os.path.join(rc_path, '.zshrc'), 'w')
    zshrc.write('source \$HOME/.zshrc\n')
    zshrc.write(new_path)
    zshrc.write('export MYVIMRC="%s"\n' % os.path.join(new_vim, '.vimrc'))
    zshrc.close()

    bashrc = open(os.path.join(rc_path, '.bashrc'), 'w')
    bashrc.write('source \$HOME/.bashrc\n')
    bashrc.write(new_path)
    bashrc.write('export MYVIMRC="%s"\n' % os.path.join(new_vim, '.vimrc'))
    bashrc.close()


def main():
    ensure_dir(cora_path)
    url = os.environ.get("CORA_URL")
    username = os.environ.get("CORA_USERNAME")

    if not url and not username:
        error("need to specify an HTTP repo and a name or just a name")
        error("like:")
        error("    cora http://github.com/username/dotfiles alfredo")
        error("or:")
        error("    cora alfredo")
        raise SystemExit()

    if not url and username in os.listdir(cora_path):
        clone_destination = os.path.join((os.path.join(cora_path, username)), "repo")
        return make_virtualenv(clone_destination)

    if url and username:
        clone_destination = os.path.join(os.path.join(cora_path, username), "repo")
        if not looks_like_url(url):
            if not os.path.exists(url):
                raise SystemExit("first argument does not look like an url and is not a path: %s" % url)
            ensure_dir(os.path.join(cora_path, username))
            run(["cp", "-r", url, clone_destination])

        else:
            run(["git", "clone", url, clone_destination])
            os.chdir(clone_destination)
            run(["git", "submodule", "update", "--init", "--recursive"])

        return make_virtualenv(clone_destination)

    if username and not url:
        if username not in os.listdir(cora_path):
            error('a virtual runtime does not exist for user: %s' % username)
            error('create a new one with: "cora [url|dir] username"')

if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if str(exc):
            error('%s: %s\n' % (exc.__class__.__name__, exc))
        else:
            error('%s\n' % (exc.__class__.__name__))
        sys.exit(1)
    except KeyboardInterrupt:
        error('cancelling via Ctrl-C')
        sys.exit(1)
