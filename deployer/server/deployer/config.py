import ConfigParser

CONF = None


def get_config(filename=None):
    global CONF
    if CONF is None:
        if filename is None:
            raise RuntimeError('No filename provided')
        CONF = ConfigParser.ConfigParser()
        CONF.read(filename)
    return CONF
