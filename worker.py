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

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='logs', queue=queue_name)

mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_HOST}:27017/")
db = mongo_client["test"]
collection = db["logs"]


def callback(ch, method, properties, body):
    log = {"message": body.decode(), "timestamp": properties.timestamp}
    collection.insert_one(log)
    print(f" [x] Saved {log}")


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for logs. To exit press CTRL+C')
channel.start_consuming()