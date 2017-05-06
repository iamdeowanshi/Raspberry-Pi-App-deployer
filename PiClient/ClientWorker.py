import os
import logging
import logging.handlers
import pika,uuid
from VirtualEnv import VirtualEnvHandler, cleanupVirtualEnvHandler
from GitRepoHandler import gitClone

#GIT_URL = 'https://github.com/amitakamat/Sample-Python-App'

def _configure_logging():
    log_filename = '/tmp/virtenvlogfile'
    root_logger = logging.RootLogger

    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024 * 5, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M')
    handler.setFormatter(formatter)

    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)

    logging.getLogger("VirtualEnv").setLevel(logging.INFO)
    logging.getLogger("GitRepoHandler").setLevel(logging.INFO)


def getPyFile(PyFileDir):
    for pyfile in os.listdir(PyFileDir):
        if pyfile.endswith(".py"):
            return os.path.join(PyFileDir+"/", pyfile)


def work(gitURL):
    venvHdl = VirtualEnvHandler()
    venvDir = venvHdl.getVenvDir()

    repoName = gitURL.split('/')[-1]
    gitRepoDir = venvDir + '/' + repoName
    gitClone(gitRepoDir, gitURL)

    reqFile = gitRepoDir + '/' + 'requirements.txt'

    venvHdl.installReqsInVirtualEnv(reqFile)

    pyFile = getPyFile(gitRepoDir)
    ret = venvHdl.testAppInVirtualEnv(cmdargs=['python', pyFile])

    cleanupVirtualEnvHandler(venvHdl)
    return ret


_configure_logging()
# if work(GIT_URL) == True:
#    print "Pass"

def OnDeployRequest(ch, method, props, body):
    deploySuccess = work(body)
    if deploySuccess:
        response = "success!"
    else:
        resopnse = "Oops! Something went wrong"

    ch.basic_publish(exchange='',
                      routing_key='pi_ip',
                      properties=pika.BasicProperties(
                                   correlation_id = props.correlation_id,
                                ),
                      body=response)



############################################## Pika Connection ##################################################


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

result = channel.queue_declare(queue='pi2')

PiQueue = result.method.queue

corr_id = str(uuid.uuid4())

#channel.basic_consume(OnResponse, queue=callback_queue)

channel.basic_publish(exchange='',
                      routing_key='pi',
                      properties=pika.BasicProperties(
                                   reply_to = PiQueue,
                                   correlation_id = corr_id,
                                ),
                      body='Request for connection')

print(" Requested ")

channel.basic_consume(OnDeployRequest, queue=PiQueue,no_ack=True)

channel.start_consuming()
#connection.close()

