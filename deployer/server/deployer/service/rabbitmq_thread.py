from deployer.common import constants
from uuid import uuid4
import logging
import pika
import threading

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
        self.rabbit_channel.queue_declare(constants.MAIN_QUEUE)
        self.cache_lock = threading.Lock()
        self.main_thread = None
        # Fake data for initial testing
        # TODO(amitakamat): Remove this
        self.connected_pi = {
            "10.4.99.199": {
                "packages": [{
                    "url" : "https://github.com/amitakamat/fake.git",
                    "status": constants.STATUS_APP_OK}],
                "ip": "10.4.99.199"
            },
            "10.4.99.198": {
                "packages": [],
                "ip": "10.4.99.198"
            },
            "10.4.99.200": {
                "packages": [{"url": "https://github.com/amitakamat/fake.git",
                              "status": constants.STATUS_APP_OK},
                             {"url": "https://github.com/siddharth/fake.git",
                              "status": constants.STATUS_INSTALLING}],
                "ip": "10.4.99.200"
            }
        }

    def create_queue(self, pi_ip):
        result = None
        pi_id = str(uuid4())
        with self.cache_lock:
            self.connected_pi[pi_id] = {
                'packages': [],
                'ip': pi_ip,
                'status': constants.STATUS_EMPTY
            }
        try:
            self.rabbit_channel.queue_declare(pi_ip)
            result = True
        except Exception as ex:
            LOG.exception('Exception processing PI: %s', pi_ip)
            result = False
        return result

    def list_connected(self):
        result = None
        with self.cache_lock:
            result = self.connected_pi.keys()
        return result

    def get_status(self, pi_id):
        with self.cache_lock:
            if pi_id not in self.connected_pi:
                return None
            pi_info = self.connected_pi[pi_id]
            return pi_info

#    def add_package_to_pi(self, pi_ip, url):
#        with self.cache_lock:
#            if pi_ip not in self.connected_pi:
#                return None
#            pi_info = self.connected_pi[pi_ip]
#            for package in pi_info['packages']:
#                if package['url'] == url:
#                    return constants.STATUS_INSTALLING
#            pi_info['packages'].append({'url': url,
#                                'operation': })
#
        
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
            self.rabbit_channel.basic_consume(self.register, queue=constants.MAIN_QUEUE)
            LOG.info('Starting consume on rabbit thread')
            self.rabbit_channel.start_consuming()
            LOG.info('Something really bad happened and rabbit consumption stopped')
        self.main_thread = threading.Thread(target=start_consume, name="rabbit_main")
        self.main_thread.start()


def get_rabbit_server(config=None):
    global RABBIT
    if not RABBIT:
        if not config:
            raise RuntimeError('Rabbit server cannot be initialized without config')
        RABBIT = RabbitMain(config)
    return RABBIT
