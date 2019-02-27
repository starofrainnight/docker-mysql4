# docker-mysql4

A docker image for MySQL4

Though there exists new MySQL distributions just like MySQL5, MySQL6, there
still have lots mature program needs a MySQL4 environment.

I think MySQL4 is too old to compile as 64bits, at least I don't think it will
works perfectly while compile in 64bits mode, so we build this MySQL4 in
64bits docker image with 32bits gcc mode to ensure it will less problem when
running.

## Features

- Base on Ubuntu:18.04 LTS image
- Build MySQL4 with 32bits mode, for avoid problems if build with 64bits gcc

## Usage

```bash
docker run -it --rm  -p 3306:3306 -v /srv/mysql:/var/lib/mysql starofrainnight/mysql4
```

## Ports

- 3306 : Database Service Port

## Volumes

Data Directory: `/var/lib/mysql`

If the data directory is empty, new sub-directories `data` and `conf` will be
generated under the parent `mysql` directory.

`data` directory stored mysql database file, and `conf` at least contained a
config file for mysql4 : `my.conf` .

So the directory structure looks like:

    /var/lib/mysql
        |
        +---- data
        |       |
        |       +---- ...
        |
        +---- conf
        |      |
        |      +---- my.conf
        |
        ...

## Environment

Here are environment variables that could be set to change internal behaviors:

- TZ : The time zone settings, defaults to `Etc/UTF`
- MYSQL_ROOT_PASSWORD: Password of root user, defaults to `mysql4`

## Acknowledgement

There are similar projects in docker-hub (Search by the keyword "mysql4"), mostly forked from [Thomas Dressler's mysql4 docker project](https://github.com/Tommi2Day/mysql4) .

This project also inspired by his project, thanks!
