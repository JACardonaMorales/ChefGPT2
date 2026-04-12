FROM python:3.11-slim
WORKDIR /app
RUN pip install pika pymongo fastapi uvicorn pytest httpx pytest-mock flake8
