FROM ubuntu:bionic

RUN apt-get update && \
    apt-get install -y gnupg2 software-properties-common && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD && \
    add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe'

RUN apt-get install -y \
    net-tools \
    iputils-ping \
    iproute2 \
    netcat \
    iperf \
    curl \
    systemd \
    sawtooth \
    sawtooth-pbft-engine \
    python3-sawtooth-poet-cli \
    python3-sawtooth-poet-engine \
    python3-sawtooth-poet-families \
    python-pip \
    iw && \
    apt install sudo

RUN pip install --upgrade pip==20.3.4 && \
    pip install flask && pip install requests && \
    pip install pandas && \
    pip install pyzmq && \
    pip install pathlib

ARG IMAGE_VER=unknown

RUN rm -rf /tmp && \
    rm -rf /rest && \
    mkdir /data && \
    mkdir /data/sawtooth && \
    mkdir /tmp && \
    mkdir /poet-shared && \
    mkdir /pbft-shared

COPY rest_scripts/* /rest/
COPY sawtooth_scripts/* /sawtooth_scripts/
COPY sawtooth_scripts/bashrc_template /root/.bash_aliases
RUN chmod +x /sawtooth_scripts/* && \
    chown sawtooth:sawtooth /var/lib/sawtooth

EXPOSE 4004
EXPOSE 8008
EXPOSE 8800
EXPOSE 5050
EXPOSE 3030
EXPOSE 5000

ENV PATH="/sawtooth_scripts:/rest:${PATH}"

CMD /bin/bash
