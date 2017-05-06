import pika
import uuid
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='pi')

result = channel.queue_declare(queue='pi_ip')

callback_queue = result.method.queue

def get_app_url():
    return "https://github.com/amitakamat/Sample-Python-App"

def callback(ch,method, props, body):
    print(" [x] Received %r" % body)
    #print("Request Received...")
    response = get_app_url()
    print response

    corr_id = str(uuid.uuid4())
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                                   reply_to = callback_queue,
                                   correlation_id = corr_id
                                ),
                     body=response)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def callResult(ch,method,props,body):
    print body
	
channel.basic_consume(callback,
                      queue='pi',
                      no_ack=True)

channel.basic_consume(callResult, queue='pi_ip',no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
