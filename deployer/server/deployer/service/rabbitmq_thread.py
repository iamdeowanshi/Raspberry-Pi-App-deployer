from uuid import uuid4
import eventlet
import logging
import pika

LOG = logging.getLogger(__name__)
RABBIT = None

class RabbitMain(object):
    def __init__(self, config):
        rabbit_user = config.get('rabbit', 'username')
        rabbit_pass = config.get('rabbit', 'password')
        rabbit_host = config.get('rabbit', 'host')
        rabbit_port = 5672 if not config.has_option('rabbit', 'port') else \
                config.getint('rabbit', 'port')
        credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
        self.rabbit_conn = pika.BlockingConnection(
                pika.ConnectionParameters(rabbit_host,
                                          rabbit_port, '/',
                                          credentials))
        self.rabbit_channel = self.rabbit_conn.channel()
        self.rabbit_channel.queue_declare('register_pi')
        self.thread_running = False
        self.connected_pi = {}

    def create_queue(self, pi_ip):
        self.connected_pi[pi_ip] = {
            'packages': {}
        }
        try:
            self.rabbit_channel.queue_declare(pi_ip)
        except Exception as ex:
            LOG.exception('Exception processing PI: %s', pi_ip)
            return False
        return True

    def register(self, ch, props, body):
        pi_ip = str(body)
        LOG.info('Raspberry Pi: %s connected', pi_ip)
        response = self.create_queue(pi_ip)
        ch.basic_publish(exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id = \
                        props.correlation_id),
                body=str(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def start_server(self):
        def start_consume():
            self.rabbit_channel.basic_consume(self.register, queue='register_pi')
            LOG.info('Starting consume on rabbit thread')
            self.rabbit_channel.start_consuming()
            LOG.info('Something really bad happened and rabbit consumption stopped')
            self.thread_running = False
        if not self.thread_running:
            eventlet.greenthread.spawn(start_consume)
            self.thread_running = True


def get_rabbit_server(config):
    global RABBIT
    if not RABBIT:
        RABBIT = RabbitMain(config)
    return RABBIT
