#!/usr/bin/env python

import sys
import argparse

# Helper routine for dumping argument info
def dbgPrintAllArgs(args):
    print 'Raspberry-pi IP: %s' % args.piIp
    print 'Server IP: %s' % args.serverIp
    print 'Server port: %s' % args.serverPort
    print 'GIT repo URL: %s' % args.gitURL
    print 'Command: %s' % args.cmd


def getPiStatusHandler(args):
    pass


def getPiListHandler(args):
    pass


def deployAppHandler(args):
    pass


handlers = {
    'get_pi_status' : getPiStatusHandler,
    'get_pi_list'   : getPiListHandler,
    'deploy_app'    : deployAppHandler,
    }


def action(args):
    handlers[args.cmd](args)


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

    # We always need Pi IP. No default.
    parser.add_argument('--pi-ip', dest='piIp',
                     help='Raspberry Pi IP address')

    parser.add_argument('--server-ip', dest='serverIp',
                     default='104.196.235.71',
                     help='flask server IP address')

    parser.add_argument('--server-port', dest='serverPort',
                     default='3000',
                     help='flask server port number')

    parser.add_argument('--git-url', dest='gitURL',
                     default='https://github.com/amitakamat/Sample-Python-App',
                     help='git URL of project to deploy')

    parser.add_argument('--cmd', dest='cmd',
                     default='get_pi_list',
                     help='API action')

    args = parser.parse_args()

    # dbgPrintAllArgs(args)

    # Does the requested command have the necessary parameters?
    if argEval(args) != True:
        parser.print_help()
        return None

    return args


if __name__ =='__main__':
    args = getArgs()
    if args == None:
        sys.exit(1)
        
    action(args)
