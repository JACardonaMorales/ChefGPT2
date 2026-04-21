import pika
import boto3


def get_ssm_parameter(name, default="localhost"):
    client = boto3.client("ssm", region_name="us-east-1")
    try:
        response = client.get_parameter(Name=name)
        return response["Parameter"]["Value"]
    except Exception:
        return default


RABBITMQ_HOST = get_ssm_parameter("/chefgpt/dev/rabbitmq/public_ip")

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()

# Declare the queue (idempotent: only creates if it doesn't exist)
channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')

print(" [x] Sent 'Hello World!'")
connection.close()
