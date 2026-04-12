from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import pymongo
import boto3
from botocore.exceptions import ClientError


def get_ssm_parameter(name: str, default: str = "localhost") -> str:
    client = boto3.client("ssm", region_name="us-east-1")
    try:
        response = client.get_parameter(Name=name)
        return response["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            print(f"[WARN] Parámetro '{name}' no encontrado. Usando: '{default}'")
            return default
        raise


RABBITMQ_HOST = get_ssm_parameter("/chefgpt/dev/rabbitmq/public_ip")
MONGODB_HOST  = get_ssm_parameter("/chefgpt/dev/mongodb/public_ip")

app = FastAPI(
    title="RabbitMQ Logger API",
    description="API para emitir logs a RabbitMQ y consultarlos desde MongoDB",
    version="2.0.0"
)

mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_HOST}:27017/")
db = mongo_client["test"]
collection = db["logs"]


def get_channel():
    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
    return connection, connection.channel()


class LogMessage(BaseModel):
    message: str


@app.get("/")
def root():
    return {"status": "ok", "service": "RabbitMQ Logger API"}


@app.post("/logs", summary="Emitir un log a RabbitMQ")
def emit_log(log: LogMessage):
    try:
        connection, channel = get_channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        channel.basic_publish(exchange='logs', routing_key='', body=log.message)
        connection.close()
        return {"status": "sent", "message": log.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs", summary="Consultar logs guardados en MongoDB")
def get_logs():
    logs = list(collection.find({}, {"_id": 0}))
    return {"total": len(logs), "logs": logs}


@app.delete("/logs", summary="Limpiar todos los logs de MongoDB")
def delete_logs():
    result = collection.delete_many({})
    return {"deleted": result.deleted_count}