#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Build MySQL4 with 32bits gcc
#
# You must prepare gcc that could support compile 32bits programs if using
# 64bits toolchain.
#
# For example (Ubuntu 18.04) :
#
# apt-get install -y build-essential gcc-multilib g++-multilib
#

import os
import click
import os.path


def exec_cmd(cmd):
    click.echo("* EXECUTE: %s" % cmd.strip())
    return os.system(cmd)


def exec_batch(cmds):
    if isinstance(cmds, str):
        cmds = cmds.split("\n")

    for cmd in cmds:
        if cmd.strip():
            exec_cmd(cmd)


def main():
    """Build MySQL4 Project
    """

    # Build bison first, MySQL4 not supported bison 3.x !

    # Unpack bison sources
    cmds = """
    wget http://ftp.gnu.org/gnu/bison/bison-2.7.tar.gz
    tar xvf bison-2.7.tar.gz
    """
    exec_batch(cmds)

    # Build bison
    os.chdir("bison-2.7")
    cmds = """
    ./configure
    make
    make install
    """
    exec_batch(cmds)
    os.chdir("..")

    # Build MySQL4
    cmds = """
    mkdir -p /var/lib/mysql/data /var/lib/mysql/log
    git clone --depth=1 https://github.com/starofrainnight/mysql-server4.git mysql
    """
    exec_batch(cmds)

    os.chdir("mysql")

    # Don't check missing!
    with open("missing", "w") as f:
        f.write(
            """#!/bin/sh
            exit 0
            """
        )

    cmds = """
    ./configure --localstatedir=/var/lib/mysql/data CFLAGS='-m32' CXXFLAGS='-m32'
    make
    make install
    pwd
    cp ./support-files/my-medium.cnf /etc/my.cnf
    """
    exec_batch(cmds)

    # Fix permissions
    exec_batch("chown -R mysql:mysql /var/lib/mysql")


if __name__ == "__main__":
    main()

