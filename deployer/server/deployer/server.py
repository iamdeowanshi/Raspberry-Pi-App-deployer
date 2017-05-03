#from eventlet import wsgi
#from paste.deploy import loadapp
from service.rabbitmq_thread import get_rabbit_server
from wsgi import start_app
import argparse
import config
import threading
#import eventlet
import logging
import logging.handlers

#eventlet.monkey_patch()


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


#def start_server(conf, paste_ini):
#    _configure_logging(conf)
#    if paste_ini:
#        paste_file = paste_ini
#    else:
#        paste_file = conf.get("DEFAULT", "paste-ini")
#    wsgi_app = loadapp('config:%s' % paste_file, 'main')
#    wsgi.server(eventlet.listen(('', conf.getint("DEFAULT", "listen_port"))), wsgi_app)

def start_rabbit_server():
    rabbit_server = get_rabbit_server(conf)
    rabbit_server.start_server()


if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = config.get_config(parser.config_file)
    _configure_logging(conf)
    flask_thread = threading.Thread(target=start_app, name='flask', args=(conf,))
    rabbit_thread = threading.Thread(target=start_rabbit_server, name='rabbit')
    try:
        flask_thread.start()
        rabbit_thread.start()
        flask_thread.join()
        rabbit_thread.join()
    except:
        print "exit"
    #rserver = get_rabbit_server(conf)
    #rserver.start_server()
    #start_server(conf, parser.paste_file)

