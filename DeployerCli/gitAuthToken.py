import requests
import json
import getpass
from requests.auth import HTTPBasicAuth
import string
import random

'''
# Function to test webhook create
def callwebhook(user_name, repo_name, TOKEN):
    payload = {
              "name"    : "web",
              "active"  : True,
              "events": [ "push" ],
              "config": {
                  #"url": "https://104.196.235.71/deployer/v1/webhookresponse",
                  "url": "https://104.196.235.71/webhook",
                  "content_type" : "json"
                  }
              }
    print json.dumps(payload)

    headers = {'Authorization' : 'basic ' + TOKEN}
    url = 'https://api.github.com/repos/' + user_name + '/' + repo_name + '/hooks'
    print url
    response_data = requests.post(url, data=json.dumps(payload), headers = headers)

    response_data.encoded='ISO-8859-1'
    print response_data.text
'''

''' Generate a unique note for every authorization token request '''
def uniqueNoteGenerator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


''' Request for Authorization token '''
def getAuthToken():
    username = raw_input('Github username: ')
    password = getpass.getpass('Github password: ')

    # Used with callwebhook
    # reponame = raw_input('Github repo name: ')

    url = 'https://api.github.com/authorizations' 

    # 'note' should be unique for every auth token request
    note = uniqueNoteGenerator()

    # 'note' is required in every request.
    #  rest of the parameters are optional
    payload = {
                  "scopes": [
                      "public_repo"
                  ],
                  "note": note
              }
    # authenticate with username and password
    res = requests.post(url,
                        auth = HTTPBasicAuth(username, password),
                        data = json.dumps(payload)
                       )

    res.encoded='ISO-8859-1'
    res = json.loads(res.content)
    keys = res.keys()

    # upon unsuccessful request, a message is returned
    if 'message' in keys:
        return None

    # upon successful request, a timestamp is generated in the field 'created_at'
    elif 'created_at' in keys:
        auth_token = res['token']

    # callwebhook(username, reponame, auth_token)

    return auth_token

if __name__ == '__main__':
    auth_tok = getAuthToken()
    if auth_tok == None:
        print "Failure. Authorization token not received"
    else:
        print "Success. Authorization token received"
