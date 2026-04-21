#!/bin/bash
exec > /var/log/install_worker.log 2>&1

echo "[1] Updating packages..."
dnf update -y
dnf install -y python3 python3-pip git

echo "[2] Installing Python dependencies..."
pip3 install pika pymongo boto3 fastapi uvicorn

echo "[3] Cloning repo..."
rm -rf /app
git clone https://github.com/JACardonaMorales/ChefGPT2.git /app

echo "[4] Starting worker..."
cd /app
PYTHONUNBUFFERED=1 nohup python3 worker.py >> /var/log/worker.log 2>&1 &

echo "[5] Done. Worker PID: $!"
