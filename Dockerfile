FROM ubuntu:18.04
LABEL maintainer="Hong-She Liang <starofrainnight@gmail.com>"

ENV TZ 'Etc/UTC'
ENV LANG C.UTF-8
ENV HOSTNAME mysql4
ENV PATH /usr/local/mysql/bin:$PATH
# Disable interactive for tzdata or dpkg-reconfigure
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update --fix-missing
RUN apt-get install --no-install-recommends -y --fix-missing \
    apt-utils tzdata locales-all \
    python3 python3-distutils python3-distutils-extra \
    build-essential gcc-multilib g++-multilib \
    lib32ncurses5 lib32ncurses5-dev libtool-bin \
    less nano git wget

RUN wget https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py \
    && rm get-pip.py

RUN pip install -U setuptools
RUN easy_install -U pip
RUN pip install -U wheel
RUN pip install -U click

# Add MySQL user and group
RUN groupadd -r mysql && useradd -r -g mysql mysql

# Compile MySQL4 from source
RUN mkdir -p /tmp/build
WORKDIR /tmp/build
COPY build-mysql.py .
RUN chmod +x *.py
RUN python3 ./build-mysql.py

# Removed unused packages
RUN apt-get purge -y --auto-remove git build-essential lib32ncurses5-dev
RUN apt-get clean

# Copy application files
COPY app /opt/docker-mysql4/
WORKDIR /opt/docker-mysql4
RUN chmod a+x *.py
RUN chmod a+x *.sh
RUN cp -rf /tmp/build/mysql/support-files/ .

# Clean up
RUN rm -rf /tmp/build

VOLUME ["/var/lib/mysql"]
EXPOSE 3306

ENTRYPOINT [ "/usr/bin/python3", "start.py" ]
