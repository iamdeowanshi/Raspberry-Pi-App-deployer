from deployer.common import constants
from uuid import uuid4
from rabbitmq_client import RabbitRpcClient as rpc_client
import json
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
        self.url_to_pi_connection = {
        }

    def create_queue(self, pi_ip):
        result = None
        with self.cache_lock:
            self.connected_pi[pi_ip] = {
                'packages': [],
                'ip': pi_ip,
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

    def get_status(self, pi_ip):
        with self.cache_lock:
            if pi_ip not in self.connected_pi:
                return None
            pi_info = self.connected_pi[pi_ip]
            return pi_info

    def add_package_to_pi(self, pi_ip, url, is_webhook_call):
        with self.cache_lock:
            if pi_ip not in self.connected_pi:
                return None
            pi_info = self.connected_pi[pi_ip]
            if not is_webhook_call:
                for package in pi_info['packages']:
                    if package['url'] == url:
                        return constants.STATUS_DUPLICATE
            self.connected_pi[pi_ip]['packages'].append(
                    {'url': url,
                     'status': constants.STATUS_INSTALLING})
        def _make_request():
            deployer_rpc = rpc_client(self.rabbit_conn, url, pi_ip)
            response = deployer_rpc.call()
            resp_obj = json.loads(response)
            with self.cache_lock:
                for pkg in self.connected_pi[pi_ip]['packages']:
                    if pkg['url'] == url:
                        if resp_obj['status']:
                            pkg['status'] = constants.STATUS_APP_OK
                        else:
                            pkg['status'] = constants.STATUS_ERROR
                        pkg['message'] = resp_obj['message']
        threading.Thread(target=_make_request).start()

    def add_pi_to_url(self, pi_ip, url):
        with self.cache_lock:
            if url not in self.url_to_pi_connection:
                self.url_to_pi_connection[url] = []
            self.url_to_pi_connection[url].append(pi_ip)

    def get_ip_for_urls(self, url):
        with self.cache_lock:
            return self.url_to_pi_connection[url]

    def register(self, ch, method, props, body):
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
