from fabric.context_managers import settings
from fabric.api import run
import sys

# IP address of the machine we are going to run commands on
#host_ip = '192.168.0.1'
# Port number of which SSH server is running. Default is 22.
#host_port = '5000'

# Connection string is <host_ip_or_hostname>:<host_port>
#host_connection_string = '%s:%s' % (host_ip, host_port)

# the command we want to run on the remote server.
remote_commands = ['hostname', 'install pip', 'ls']


def run_command():
    with settings(host_string=sys.argv[1], user=sys.argv[2], password=sys.argv[3]):
        with settings(warn_only=True):
            for command in remote_commands:
                result = run(command)
                if result.succeeded:
                    print('Command ' + command + ' executed successfully')
                else:
                    print('Command ' + command + ' execution failed')
                #print('Command ' + command + ' Status Succeeded : ' + str(result.succeeded))
                #print('Command ' + command + ' Status failed : ' + str(result.failed))

if __name__ == "__main__":
    run_command()
