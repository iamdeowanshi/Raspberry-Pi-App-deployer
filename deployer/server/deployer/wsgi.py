from flask import abort 
from flask import Flask
from flask import request
from service.rabbitmq_thread import get_rabbit_server
import json
import logging
import sys
import requests

LOG = logging.getLogger(__name__)

JSON_DATA = """
{
  "name": "web",
  "active": true,
  "events": [
    "push"
  ],
  "config": {
    "url": "http://104.196.235.71/deployer/v1/webhookresponse",
    "content_type": "json"
  }
}
"""

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
    if not json_data.get('git_url'):
        result = {"result": "error", "message": "Invalid request: git_url absent"}
        return json.dumps(result)
    if not json_data.get('code'):
        result = {"result": "error", "message": "Invalid request: code absent"}
        return json.dumps(result)
    if not json_data.get('type'):
        result = {"result": "error", "message": "Invalid request: type absent"}
        return json.dumps(result)
    repo_url = json_data.get('git_url')
    repo_array = str(repo_url).split("/")
    user_name = repo_array[3]
    repo_name = repo_array[4]
    code_data = json_data.get('code')
    type_data = json_data.get('type')
    if type_data == "cli":
        read_hooks(user_name,repo_name, code_data)
        rserver.add_pi_to_url(pi_ip, json_data.get('git_url'))
    if type_data == "web":
        try:
            token = get_Access_Token(code_data)
            read_hooks(repo_name, token)
            rserver.add_pi_to_url(pi_ip, json_data.get('git_url'))
        except:
            LOG.info('Failed to get access token.')

    rserver.add_package_to_pi(pi_ip, json_data.get('git_url'), False)
    result = {"result": "success", "message": "Accepted request to deploy %s on %s" % (json_data['git_url'], pi_ip)}
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

def read_hooks(user_name, repo_name, TOKEN):
    '''checking for webhooks'''
    hook_url = "http://104.196.235.71/deployer/v1/webhookresponse"
    headers = {'Authorization' : 'token ' + TOKEN}
    url = 'https://api.github.com/repos/' + user_name + '/' + repo_name + '/hooks'
    response_data = requests.get(url, headers = headers)
    resp = json.loads(response_data.content)
    count = 0
    for index in xrange(len(resp)):
        if hook_url == resp[index]['config']['url']:
            count += 1
            LOG.info('Repository already has a server webhook. Using the existing webhook')
            break
    if count == 0:
        LOG.info('Repository does not have server webhook. Adding webhook.')
        add_hook(user_name,repo_name, TOKEN)

def add_hook(user_name, repo_name, TOKEN):
    ''' Add hook to github repo'''
    headers = {'Authorization' : 'token ' + TOKEN}
    url = 'https://api.github.com/repos/' + user_name + '/' + repo_name + '/hooks'
    response_data = requests.post(url, JSON_DATA, headers = headers)
    LOG.info('Add webhook response : ' + str(response_data.content))

def get_Access_Token(code):
    '''Fetching access token from github'''
    headers = {"Content-type" : "application/json"}
    data = '{"code":"' + code + '","client_id": "9ef838536d7516d3ab56","client_secret":"a6db61f6620ac50e96dd93193c02e753fb91d1ea"}'
    url = 'https://github.com/login/oauth/access_token'
    response_data = requests.post(url, data, headers=headers)
    resp_array = str(response_data.content).split("=")
    token = resp_array[1].split("&")[0]
    LOG.info('Get access token response : ' + str(response_data.content))
    return token

def app_factory(global_config, **local_conf):
    return app

def start_app(conf):
    rserver = get_rabbit_server(config=conf)
    LOG.info('Starting rabbit server')
    rserver.start_server()
    LOG.info('Starting flask app...')
    port = conf.getint("DEFAULT", "listen_port")
    app.run(host='0.0.0.0', port=port)
