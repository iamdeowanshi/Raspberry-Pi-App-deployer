from ConfigParser import ConfigParser


CONF = None

def get_config(config_filename):
    global CONF
    if CONF is None:
        CONF = ConfigParser()
        CONF.read(config_filename)
    return CONF
