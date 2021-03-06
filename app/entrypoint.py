#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import click
import time
import glob
import os.path
import subprocess
from configparser import ConfigParser


def safe_copy_mysql_conf(data_dir):
    # Copy default config file to volume if user does not provided one
    default_cnf_path = "/opt/docker-mysql4/support-files/my-medium.cnf"
    if not glob.glob("/etc/mysql/conf.d/*.cnf"):
        os.system("cp %s %s" % (default_cnf_path, "/etc/mysql/conf.d/"))


def mysql_initialize():
    data_dir = "/var/lib/mysql"
    hostname = os.environ.get("HOSTNAME", "mysql4")
    password = os.environ.get("MYSQL_ROOT_PASSWORD", "mysql4")

    with open("/etc/hosts", "r+") as f:
        if not hostname in f.read():
            f.write("127.0.0.1 %s\n" % hostname)

    os.makedirs("%s" % data_dir, exist_ok=True)

    os.system("chown -R mysql:mysql %s" % data_dir)

    # Ensure correct timezone
    os.system("bash /opt/docker-mysql4/update-tz.sh")

    safe_copy_mysql_conf(data_dir)

    try:
        have_file = os.listdir("%s" % data_dir)
    except FileNotFoundError:
        have_file = False

    if not have_file:
        click.echo("Initializing database...")
        os.system("mysql_install_db --user=mysql")

        click.echo("Setting root password...")
        os.system("mysqld_safe --skip-networking &")

        time.sleep(5)

        # Enable full network access
        sql = r"""SET @@SESSION.SQL_LOG_BIN=0;
        DELETE FROM user where host in ('localhost','{hostname}');
        GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{password}';
        FLUSH PRIVILEGES ;
        """.format(
            hostname=hostname, password=password
        )

        subprocess.run(["mysql", "-Uroot", "mysql"], input=sql.encode("utf-8"))

        time.sleep(5)

        pid_files = glob.glob("%s/*.pid" % data_dir)
        if pid_files:
            pid_file_path = pid_files[0]
            with open(pid_file_path) as f:
                pid = f.read().strip()

            os.system("kill %s" % pid)

            time.sleep(5)


def main():
    if len(sys.argv) <= 1:
        return

    if sys.argv[1] == "mysqld_safe":
        mysql_initialize()

    return subprocess.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
