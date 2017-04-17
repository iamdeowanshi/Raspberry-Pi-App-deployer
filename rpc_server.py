import pika
credentials = pika.PlainCredentials('amita', 'amita')
connection = pika.BlockingConnection(pika.ConnectionParameters('104.196.235.71', 5672, '/', credentials))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


def get_app_url():
    return "https://github.com/amitakamat/Amita-Kamat-CMPE-273/blob/master/CMPE-273-Assignment-1/requirements.txt"

def on_request(ch, method, props, body):

    print("Request Received...")
    response = get_app_url()

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()