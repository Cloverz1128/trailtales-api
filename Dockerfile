# Base image
FROM ubuntu:18.04

# Set non-interactive mode to prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies and development tools
RUN apt-get update && apt-get install -y \
    wget gnupg lsb-release curl \
    debconf-utils software-properties-common \
    vim sudo rsync dos2unix iproute2 \
    python3 python3-pip python3-dev \
    pkg-config libgirepository1.0-dev libcairo2-dev \
    openssh-server tree \
    lsof net-tools

# Download and install MySQL APT repository configuration (non-interactively)
RUN wget https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb && \
    echo "mysql-apt-config mysql-apt-config/select-server select mysql-8.0" | debconf-set-selections && \
    dpkg -i mysql-apt-config_0.8.15-1_all.deb || true

# Add missing GPG key and install MySQL
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C && \
    apt-get update || apt-get update && \
    apt-get install -y mysql-server libmysqlclient-dev

# Set python3 as the default python command
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Create a development user and set default login directory
RUN useradd -ms /bin/bash penny && \
    echo "penny ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    echo "cd /twitter-api" >> /home/penny/.bashrc

# Set the working directory
WORKDIR /twitter-api

# Copy Python dependencies file
COPY requirements.txt /twitter-api/requirements.txt

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Copy MySQL initialization script and make it executable
COPY init_mysql.sh /init_mysql.sh
RUN chmod +x /init_mysql.sh

# Default command: start MySQL service and open bash shell
CMD service mysql start && bash
