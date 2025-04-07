#!/bin/bash

mysql -u root << EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'P@sSw0rD';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS twitter;
EOF
