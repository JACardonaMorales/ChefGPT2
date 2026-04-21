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

# We use a 'fanout' exchange to broadcast to everyone
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)

print(f" [x] Sent {message}")
connection.close()
