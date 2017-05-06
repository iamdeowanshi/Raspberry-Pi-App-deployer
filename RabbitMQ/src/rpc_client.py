import pika
import uuid
import subprocess
import os
from backports import tempfile

class RpcClient(object):
    def __init__(self):
        credentials = pika.PlainCredentials('amita', 'amita')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('104.196.235.71', 5672, '/', credentials))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.replace("blob", "raw")
        self.install_dependencies()

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='register_pi',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body="")
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def get_repo_name(self):
        split_array = self.response.split("/")
        return split_array[len(split_array) - 1]

    def get_app_file(self, temp_dir_loc):
        for file in os.listdir(temp_dir_loc):
            if file.endswith(".py"):
                return file

    def install_dependencies(self):
        repo_name = self.get_repo_name()
        print repo_name
        temp_dir_loc = ''

        #f = tempfile.TemporaryDirectory()
        with tempfile.TemporaryDirectory() as f:
            temp_dir_loc = f
            if os.path.exists(temp_dir_loc):
                print "Temporary directory created.."
            else:
                print "Error : Temporary directory could not be created."

            #p = subprocess.Popen('pip install -r ' + self.response, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            path = self.response + ' ' + temp_dir_loc
            p = subprocess.call('git clone ' + path, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            if p == 0:
                print "Cloning Successful.."
                print "Installing Packages.."
                p = subprocess.call('sudo pip install -r ' + temp_dir_loc + '/requirements.txt', shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
                if p == 0:
                    print "Packages installed successfully.. "
                    print "Running App.. "
                    file_name = self.get_app_file(temp_dir_loc)
                    p = subprocess.call('python ' + temp_dir_loc + '/' + file_name, shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                    if p == 0:
                        print "App run successfully.."
                        '''p = subprocess.call('sudo rm -r ' + repo_name + '/', shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)'''
                    else:
                        print "Error: Could not run app"
                else:
                    print "Error: Packages could not be installed.."
            else:
                print "Clone Unsuccessful.."

        if not os.path.exists(temp_dir_loc):
            print "Temporary directory removed.."
        else:
            print "Error : Temporary directory could not be removed."

deployer_rpc = RpcClient()

print(" [x] Requesting")
response = deployer_rpc.call()
print(" [.] Got %r" % response)
