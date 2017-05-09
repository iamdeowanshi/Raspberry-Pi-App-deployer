from flask import abort 
from flask import Flask
from flask import request
from service.rabbitmq_thread import get_rabbit_server
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


@app.route('/v1/<pi_ip>/status', methods=['GET'])
def details(pi_ip):
    rserver = get_rabbit_server()
    result = rserver.get_status(pi_ip)
    if result is None:
        # PI not found, raise 404
        abort(404)
    return json.dumps(result)


@app.route('/v1/list', methods=['GET'])
def pi_list():
    rserver = get_rabbit_server()
    return json.dumps(rserver.list_connected())


@app.route('/v1/<pi_ip>/deploy', methods=['POST', 'PUT'])
def deploy(pi_ip):
    rserver = get_rabbit_server()
    try:
        data = request.data
        LOG.info('Data: %s', data)
        json_data = json.loads(data)
    except:
        result = {"result": "error", "message": "Invalid JSON Object"}
        return json.dumps(result)
    if json_data.get('git_url'):
        rserver.add_package_to_pi(pi_ip, json_data.get('git_url'), False)
        result = {"result": "success", "message": "Accepted request to deploy %s on %s" % (json_data['git_url'], pi_ip)}
        rserver.add_pi_to_url(pi_ip, json_data.get('git_url'))
        return json.dumps(result)
    else:
        result = {"result": "error", "message": "Invalid request: git_url absent"}
        return json.dumps(result)

@app.route('/v1/webhookresponse', methods=['POST', 'PUT'])
def webhookcall():
    data = request.data
    json_data = json.loads(data)
    LOG.info('Data: %s', data)
    rserver = get_rabbit_server()
    if json_data['repository']:
        url = json_data['repository']['html_url']
        LOG.info('URL: %s', url)
        if url:
            ip_list = rserver.get_ip_for_urls(url)
            LOG.info(json.dumps(ip_list))
            for ip in ip_list:
                LOG.info('IP: %s', ip)
                rserver.add_package_to_pi(ip, url, True)
                LOG.info('Webhook Call for %s added for pi %s', url, ip)
            result = {"result":"webhook call successful"}
        else :
            result = {"result" : "Webhook call made. No URL available."}
    else :
        result ={"result" : "Webhook call made. No repository details present."}
    return json.dumps(result)


def app_factory(global_config, **local_conf):
    return app

def start_app(conf):
    rserver = get_rabbit_server(config=conf)
    LOG.info('Starting rabbit server')
    rserver.start_server()
    LOG.info('Starting flask app...')
    port = conf.getint("DEFAULT", "listen_port")
    app.run(host='0.0.0.0', port=port)
