import pika
import time

RABBITMQ_HOST = "localhost"
EXCHANGE = "patient.updates"
ROUTING_KEY = "patient.created"
QUEUE = "patient.created"

def test_publish_and_consume_patient_message():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    # Declare exchange and queue (idempotent)
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)

    # Publish a test message
    message_body = '{"patient_id": 123, "name": "Test Patient"}'
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=ROUTING_KEY,
        body=message_body,
        properties=pika.BasicProperties(content_type="application/json")
    )
    print("Published test message.")

    # Try to consume the message
    method_frame, header_frame, body = channel.basic_get(queue=QUEUE, auto_ack=True)
    assert body is not None, "No message received from queue!"
    assert body.decode() == message_body, f"Received: {body.decode()}"

    print(f"Consumed message: {body.decode()}")

    # Clean up
    connection.close()

if __name__ == "__main__":
    test_publish_and_consume_patient_message()