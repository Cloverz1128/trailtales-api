FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget gnupg lsb-release curl \
    debconf-utils software-properties-common \
    vim sudo rsync dos2unix iproute2 \
    python3 python3-pip python3-dev \
    pkg-config libgirepository1.0-dev libcairo2-dev \
    libmysqlclient-dev \
    openssh-server tree \
    lsof net-tools \
    memcached

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN useradd -ms /bin/bash penny && \
    echo "penny ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    echo "cd /twitter-api" >> /home/penny/.bashrc

WORKDIR /twitter-api

COPY requirements.txt /twitter-api/requirements.txt

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

CMD ["bash"]
