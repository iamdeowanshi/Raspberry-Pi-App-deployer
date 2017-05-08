''' Sample application for webhook'''
import sys
import getpass
import requests
import base64
import json

USERNAME = ""
PASSWORD = ""

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

TOKEN = base64.urlsafe_b64encode("%s:%s" % (USERNAME, PASSWORD))
repo_array = str(sys.argv[1]).split("/")
repo_name = repo_array[4]

def read_hooks():
    '''checking for webhooks'''
    hook_url = "http://104.196.235.71/deployer/v1/webhookresponse"
    headers = {'Authorization' : 'Basic ' + TOKEN}
    url = 'https://api.github.com/repos/' + "iamdeowanshi" + "/" + repo_name + "/hooks"
    response_data = requests.get(url, headers=headers)
    resp = json.loads(response_data.content)
    count = 0
    for index in xrange(len(resp)):
        if hook_url == resp[index]['config']['url']:
            count += 1
            print "repo has server webhook"
            break

    if count == 0:
        print "attach webhook"
        add_hook()

def add_hook():
    ''' Add hook to github repo'''
    headers = {'Authorization' : 'Basic ' + TOKEN}
    url = 'https://api.github.com/repos/' + "iamdeowanshi" + "/" + repo_name + "/hooks"
    response_data = requests.post(url, JSON_DATA, headers=headers)
    print response_data.content


if __name__ == "__main__":
    # USERNAME = raw_input("Github Username:")
    # PASSWORD = getpass.getpass()
    read_hooks()
