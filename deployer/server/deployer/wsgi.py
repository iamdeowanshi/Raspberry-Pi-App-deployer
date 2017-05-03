from flask import Flask
from flask import request
import json
import logging

LOG = logging.getLogger(__name__)


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
            return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)


@app.route('/v1/<uuid:pi_id>/status', methods=['GET'])
def details(pi_id):
    return "%s is happy" % pi_id


@app.route('/v1/list', methods=['GET'])
def pi_list():
    return str(['pi 1', 'pi 2'])


@app.route('/v1/<uuid:pi_id>/deploy', methods=['POST', 'PUT'])
def deploy(pi_id):
    #data = request.data
    data = None
    LOG.info('Data: %s', data)
    try:
        json_data = json.loads(data)
    except:
        return "Invalid JSON object"
    if json_data.get('git_url'):
        return 'Accepted request to deploy %s on %s' % (json_data['git_url'], pi_id)
    else:
        return 'Invalid request: param git_url absent'


def app_factory(global_config, **local_conf):
    return app

def start_app(conf):
    LOG.info('Starting flask app...')
    port = conf.getint("DEFAULT", "listen_port")
    app.run(host='0.0.0.0', port=port)
