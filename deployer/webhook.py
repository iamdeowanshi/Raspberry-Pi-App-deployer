''' Sample application for webhook'''
import sys
import getpass
import requests
import base64

USERNAME = ""
PASSWORD = ""

json = """
{
  "name": "web",
  "active": true,
  "events": [
    "push",
    "pull_request"
  ],
  "config": {
    "url": "https://48333df3.ngrok.io/payload",
    "content_type": "json"
  }
}
"""

def readHooks():
    repo_array = str(sys.argv[1]).split("/")
    repo_name = repo_array[4]
    token = base64.urlsafe_b64encode("%s:%s" % (USERNAME, PASSWORD))
    headers = {'Authorization' : 'Basic ' + token}
    url = 'https://api.github.com/repos/' + USERNAME + "/" + repo_name + "/hooks"
    response_data = requests.post(url,data=json, headers=headers)
    print response_data.content

if __name__ == "__main__":
    USERNAME = raw_input("Github Username:")
    PASSWORD = getpass.getpass()
    readHooks()
