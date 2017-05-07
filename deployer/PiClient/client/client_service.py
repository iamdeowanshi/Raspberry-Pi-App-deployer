import argparse
import logging
import logging.handlers
from common import config
from service import ClientWorker

def _configure_logging(conf):
    log_filename = conf.get('log', 'file')
    root_logger = logging.RootLogger

    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024 * 5, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
    handler.setFormatter(formatter)

    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)

    logging.getLogger("VirtualEnv").setLevel(logging.INFO)
    logging.getLogger("GitRepoHandler").setLevel(logging.INFO)
    logging.getLogger("Pika").setLevel(logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser(description='CMPE 273 Raspberry Pi Client service')
    parser.add_argument('--config-file', dest='config_file', default='/etc/deployer-client/deployer.conf')
    return parser.parse_args()


if __name__ == '__main__':
    parser = parse_args()
    conf = config.get_config(parser.config_file)
    _configure_logging(conf)
    ClientWorker.start_service(conf)
