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
    cfg = ConfigParser(allow_no_value=True)

    # Copy default config file to volume if user does not provided one
    default_cnf_path = "/opt/docker-mysql4/support-files/my-medium.cnf"
    src_cnf_path = "%s/my.cnf" % data_dir
    if not os.path.exists(src_cnf_path):
        os.system("cp %s %s" % (default_cnf_path, src_cnf_path))

    # Overwrite MySQL4 required config file
    cfg.read([src_cnf_path])

    if not cfg.has_section("mysqld"):
        cfg.add_section("mysqld")

    # Not allow specific server's port
    if cfg.has_option("mysqld", "port"):
        cfg.remove_option("mysqld", "port")

    # Set log directory, force to "log"
    if cfg.has_option("mysqld", "log-bin"):
        value = cfg.get("mysqld", "log-bin")
        if value and ((r"/" in value) or (r"\\" in value)):
            # FIXME: Value of 'log-bin' could be 'ON' and specific format by option
            # 'log_bin_basename' or 'log_bin_index'
            basename = os.path.basename(value)
            cfg.set("mysqld", "log-bin", "%s/log/%s" % (data_dir, basename))

    # Set data directory, force to "data"
    cfg.set("mysqld", "datadir", "%s/data/" % data_dir)

    # Set innodata home directory, force to "data"
    cfg.set("mysqld", "innodb_data_home_dir", "%s/data/" % data_dir)

    # Not allow to modify mysql client's port!
    if cfg.has_option("client", "port"):
        cfg.remove_option("client", "port")

    with open("/etc/my.cnf", "w") as f:
        cfg.write(f)


@click.command()
def main():
    data_dir = "/var/lib/mysql"
    hostname = os.environ.get("HOSTNAME", "mysql4")
    password = os.environ.get("MYSQL_ROOT_PASSWORD", "mysql4")

    with open("/etc/hosts", "r+") as f:
        if not hostname in f.read():
            f.write("127.0.0.1 %s\n" % hostname)

    os.makedirs("%s/data" % data_dir, exist_ok=True)

    os.system("chown -R mysql:mysql %s" % data_dir)

    # Ensure correct timezone
    os.system("bash /opt/docker-mysql4/update-tz.sh")

    safe_copy_mysql_conf(data_dir)

    try:
        have_file = os.listdir("%s/data" % data_dir)
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

        pid_files = glob.glob("%s/data/*.pid" % data_dir)
        if pid_files:
            pid_file_path = pid_files[0]
            with open(pid_file_path) as f:
                pid = f.read().strip()

            os.system("kill %s" % pid)

            time.sleep(5)

    subprocess.run(["mysqld_safe"])


if __name__ == "__main__":
    main()
