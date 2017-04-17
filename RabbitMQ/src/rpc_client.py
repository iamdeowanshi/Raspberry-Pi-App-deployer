import pika
import uuid
import subprocess

class RpcClient(object):
    def __init__(self):
        credentials = pika.PlainCredentials('amita', 'amita')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('104.196.235.71', 5672, '/', credentials))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.replace("blob", "raw")
        self.install_dependencies()

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body="")
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def install_dependencies(self):
        p = subprocess.Popen('pip install -r ' + self.response, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line

deployer_rpc = RpcClient()

print(" [x] Requesting")
response = deployer_rpc.call()
print(" [.] Got %r" % response)
