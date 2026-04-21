#!/bin/bash
set -e

dnf update -y
dnf install -y python3 python3-pip git

pip3 install pika pymongo boto3 fastapi uvicorn

# Ensure /app doesn't exist before cloning
rm -rf /app
git clone https://github.com/JACardonaMorales/ChefGPT2.git /app
cd /app

PYTHONUNBUFFERED=1 nohup python3 worker.py > /var/log/worker.log 2>&1 &
