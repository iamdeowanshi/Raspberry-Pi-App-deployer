import os
import signal
import subprocess
import logging
import shutil
from backports import tempfile
from virtualenvapi.manage import VirtualEnvironment

LOG = logging.getLogger(__name__)


TIMEOUT = 10

class VirtualEnvHandler(object):
    def __init__(self):
        self.venvDir = None
        self.venv = None

        try:
            self.venvDir = tempfile.mkdtemp()
            LOG.info("Created virtual env dir: %s", self.venvDir)
        except Exception as e:
            LOG.exception("Exception during virtual env directory create: %s", e.message)

        if not os.path.exists(self.venvDir):
            LOG.error("Failed to create virtual env dir: %s. Exiting", self.venvDir)
            return

        # create virtual env
        self.venv = VirtualEnvironment(self.venvDir)

    def isValidVenv(self):
        if self.venv != None:
            return True
        return False

    def getVenvDir(self):
        return self.venvDir

    def timeoutHandler(self, signum, frame):
        raise RuntimeError("Error")

    def installReqsInVirtualEnv(self, reqFile):
        try:
            if os.path.exists(reqFile):
                LOG.info("Installing pip packages from requirements.txt")
                self.venv.install('-r', options=[reqFile])
            else:
                # Here, 'reqFile' is the package name
                self.venv.install(reqFile)

        except Exception as e:
            LOG.exception("Error installing package(s)")
            return False

        LOG.info("Successfully installed pip packages")
        return True

    '''
    Upon successful execution of cmdargs (return value 0), output to stdout
    is returned in the variable out. A non-zero return value results in None
    being returned to the caller. A time out during execution is considered
    a success (maybe we are executing a blocking process?). An empty string
    is returned to indicate success in this case.
    '''
    def testAppInVirtualEnv(self, cmdargs=[]):
        out = None

        # If process doesn't quit in TIMEOUT seconds, raise alarm
        signal.signal(signal.SIGALRM, self.timeoutHandler)
        signal.alarm(TIMEOUT)

        try:
            # Private function. We may want to fork the project for stability.
            LOG.info("Running python application from %s", self.venvDir)
            out = self.venv._execute(cmdargs)

        except RuntimeError as e:
            LOG.info("Timed out waiting for app to finish. Exiting with success.")
            out = ''

        except Exception as e:
            LOG.exception("Exception while executing app in virtual env: %s", e.message)

        # Disable the alarm
        signal.alarm(0)
        LOG.info("Output from execution: %s", out)
        return out


def getVirtualEnvHandler():
    return VirtualEnvHandler()

def cleanupVirtualEnvHandler(venvHandler):
    shutil.rmtree(venvHandler.venvDir)

if __name__ == "__main__":
    venvHandler = VirtualEnvHandler()
    venvHandler.installReqsInVirtualEnv('')
    venvHandler.testAppInVirtualEnv()
    cleanupVirtualEnvHandler(venvHandler)
