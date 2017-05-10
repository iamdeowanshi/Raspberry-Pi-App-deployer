#!/usr/bin/env python

import sys
import argparse
import requests
import json
from gitAuthToken import getAuthToken

SUCCESS = 0
FAILURE = 1

# Helper routine for dumping argument info
def dbgPrintAllArgs(args):
    print 'Raspberry-pi IP: %s' % args.piIp
    print 'Server IP: %s' % args.serverIp
    print 'Server port: %s' % args.serverPort
    print 'GIT repo URL: %s' % args.gitURL
    print 'Command: %s' % args.cmd


def getPiStatusHandler(args):
    url = 'https://' + args.serverIp + ':' + args.serverPort + '/deployer/v1/' + args.piIp + '/status'
    response = requests.get(url, verify=False)
    response.encoding = 'ISO-8859-1'

    if response.status_code == 404:
        print 'Invalid Raspberry Pi IP address specified'
        return FAILURE

    try:
        res = json.loads(response.content)
        print "RaspberryPi IP: %s" % args.piIp
        for package in res['packages']:
            print '    Package URL: %s' % package['url']
            print '    Package Status: %s' % package['status']
            if 'message' in package:
                print '    Package Message: %s'% package['message']

        return SUCCESS

    except Exception as e:
        print 'Error processing JSON. %s' % e.message
        return FAILURE


def getPiListHandler(args):
    url = 'https://' + args.serverIp + ':' + args.serverPort + '/deployer/v1/list'
    response = requests.get(url, verify=False)
    response.encoding = 'ISO-8859-1'

    try:
        res = json.loads(response.content)
        print 'Registered Raspberry Pi(s) IP Addresses:'
        for pi in json.loads(response.content):
            print '    %s' % pi

        return SUCCESS

    except Exception as e:
        print 'Error processing JSON. %s' % e.message
        return FAILURE


def deployAppHandler(args):
    url = 'https://' + args.serverIp +  ':' + args.serverPort +  '/deployer/v1/' + args.piIp + '/deploy'

    tok = getAuthToken()

    data = {  'git_url' : args.gitURL,
              'type'    : 'cli',
              'code'    : tok
           }

    response = requests.post(url, data=json.dumps(data), verify=False)
    response.encoding = 'ISO-8859-1'

    try:
        response = json.loads(response.content)

        if response['result'] == 'success':
            print 'Successfully submitted deploy request for repo: %s' % args.gitURL
        else:
            print 'Failed to submit deploy request for repo: %s' % args.gitURL
            return FAILURE

        return SUCCESS

    except Exception as e:
        print 'Error processing JSON. %s' % e.message
        return FAILURE


handlers = {
    'get_pi_status' : getPiStatusHandler,
    'get_pi_list'   : getPiListHandler,
    'deploy_app'    : deployAppHandler,
    }


def action(args):
    return handlers[args.cmd](args)


def argEval(args):
    if args.cmd == 'get_pi_status':
        if args.piIp != None:
            return True
    elif args.cmd == 'get_pi_list':
        return True
    elif args.cmd == 'deploy_app':
        if args.piIp != None and args.gitURL != None:
            return True
    else:
        # Invalid command
        return False

    return False


def getArgs():
    parser = argparse.ArgumentParser(description='Deployer CLI.')

    parser.add_argument('--pi-ip', dest='piIp',
                     help='Raspberry Pi IP address')

    parser.add_argument('--server-ip', dest='serverIp',
                     default='104.196.235.71',
                     help='flask server IP address')

    parser.add_argument('--server-port', dest='serverPort',
                     default='443',
                     help='flask server port number')

    parser.add_argument('--git-url', dest='gitURL',
                     help='git URL of project to deploy')

    parser.add_argument('--cmd', dest='cmd',
                     default='get_pi_list',
                     help='API action')

    args = parser.parse_args()

    # Does the requested command have the necessary parameters?
    if argEval(args) != True:
        parser.print_help()
        return None

    return args


if __name__ =='__main__':
    # Disable certificate warnings
    requests.packages.urllib3.disable_warnings()

    args = getArgs()
    if args == None:
        sys.exit(FAILURE)

    sys.exit(action(args))
