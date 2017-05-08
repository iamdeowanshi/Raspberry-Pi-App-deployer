from uuid import uuid4
import json
import pika


class RabbitRpcClient(object):
    def __init__(self, connection, url, pi_ip):
        self.connection = connection
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)
        self.url = url
        self.pi_ip = pi_ip
        self.response = None
        self.corr_id = str(uuid4())

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.pi_ip,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,),
                                   body=self.url)
        while self.response is None:
            self.connection.process_data_events()
        return self.response
