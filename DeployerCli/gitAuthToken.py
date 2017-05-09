import requests
import json
import getpass
from requests.auth import HTTPBasicAuth
import string
import random

''' Generate a unique note for every authorization token request '''
def uniqueNoteGenerator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


''' Request for Authorization token '''
def getAuthToken():
    username = raw_input('Github username: ')
    password = getpass.getpass('Github password: ')
    
    url = 'https://api.github.com/authorizations' 
    note = uniqueNoteGenerator()
    # 'note' is required in every request.
    #  rest of the parameters are optional
    payload = {
                "note": note  
              }
    
    res = requests.post(url,
                        auth = HTTPBasicAuth(username, password),
                        data = json.dumps(payload))
    
    res.encoded='ISO-8859-1'
    res = json.loads(res.content)
    keys = res.keys()

    if 'message' in keys:
        return None

    elif 'created_at' in keys:
        auth_token = res['token']

    # TODO: integrate this token with the rest api call from cli

    return auth_token

if __name__ == '__main__':
    auth_tok = getAuthToken()
    if auth_tok == None:
        print "Failure. Authorization token not received"
    else:
        print "Success. Authorization token received"
