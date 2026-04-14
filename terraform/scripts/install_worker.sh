#!/bin/bash
dnf update -y
dnf install -y python3 python3-pip git

pip3 install pika pymongo boto3

git clone https://github.com/JACardonaMorales/ChefGPT2.git /app
cd /app

nohup python3 worker.py > /tmp/worker.log 2>&1 &
