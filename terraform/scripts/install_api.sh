#!/bin/bash
set -e
dnf update -y
dnf install -y python3 python3-pip git

# Instalar boto3 para Parameter Store
pip3 install fastapi uvicorn pika pymongo boto3

# Clonar el proyecto
git clone https://github.com/JACardonaMorales/ChefGPT2.00.git /app
cd /app

# Arrancar la API en el puerto 8000
nohup uvicorn api:app --host 0.0.0.0 --port 8000 &