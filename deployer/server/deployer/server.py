from common import config
from service.rabbitmq_thread import get_rabbit_server
from wsgi import start_app
import argparse
import logging
import logging.handlers


def _get_arg_parser():
    parser = argparse.ArgumentParser(description="CMPE 273 App Deployer Service")
    parser.add_argument('--config-file', dest='config_file', default='/etc/deployer/deployer.conf')
    parser.add_argument('--paste-ini', dest='paste_file', default='/etc/deployer/deployer-paste.ini')
    return parser.parse_args()


def _configure_logging(conf):
    log_filename = conf.get("log", "location")
    root_logger = logging.RootLogger
    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024 * 5, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("pika").propagate = False


if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = config.get_config(parser.config_file)
    _configure_logging(conf)
    start_app(conf)

