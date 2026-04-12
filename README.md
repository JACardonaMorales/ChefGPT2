# APIChefGPT2.00 - RabbitMQ + MongoDB + FastAPI

Proyecto de mensajería asíncrona usando RabbitMQ como message broker,
MongoDB para persistencia y FastAPI para exponer una API REST con Swagger.

## Arquitectura

[python-client] --> [RabbitMQ (fanout exchange)] --> [worker] --> [MongoDB]
^
[FastAPI /logs POST]

## Servicios

| Servicio       | Descripción                              | Puerto        |
|----------------|------------------------------------------|---------------|
| rabbitmq       | Message broker                           | 5672 / 15672  |
| mongo          | Base de datos de logs                    | 27017         |
| worker         | Consumidor de mensajes, guarda en Mongo  | —             |
| api            | REST API con Swagger                     | 8000          |
| python-client  | Cliente manual para emitir logs          | —             |

## Requisitos

- Docker
- Docker Compose

## Levantar el proyecto

```bash
docker compose up -d --build
Servicios disponibles
Swagger UI: http://localhost:8000/docs

RabbitMQ UI: http://localhost:15672 (user/password)

MongoDB: mongodb://localhost:27017

Uso
Emitir un log manualmente:

bash
docker exec -it practice4-python-client-1 python emit_logs.py
O desde Swagger en http://localhost:8000/docs usando POST /logs.

Pruebas unitarias:
docker exec -it api_service pytest test_api.py -v
Chequeo de código estático:
docker exec -it api_service flake8 .
Detener el proyecto:
docker compose down
Detener y eliminar imágenes:
docker compose down --rmi all

***
