#!/bin/bash
set -e
dnf update -y
# Instalar Erlang y RabbitMQ
dnf install -y erlang
rpm --import https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey
dnf install -y https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12.13/rabbitmq-server-3.12.13-1.el8.noarch.rpm
systemctl start rabbitmq-server
systemctl enable rabbitmq-server
# Habilitar plugin de management
rabbitmq-plugins enable rabbitmq_management
# Crear usuario de la app
rabbitmqctl add_user user password
rabbitmqctl set_user_tags user administrator
rabbitmqctl set_permissions -p / user ".*" ".*" ".*"