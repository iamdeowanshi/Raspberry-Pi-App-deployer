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

    def getVenvDir(self):
        return self.venvDir

    def timeoutHandler(self, signum, frame):
        raise RuntimeError("Error")

    def installReqsInVirtualEnv(self, reqFile):
        if os.path.exists(reqFile):
            # FIXME: This is a hack. We are passing package name as '-r'
            # and reqFile as part of the options list. This will be expanded
            # correctly though (for now).

            self.venv.install('-r', options=[reqFile])
        else:
            self.venv.install(reqFile)

    def testAppInVirtualEnv(self, cmdargs=[]):
        ret = False

        # If process doesn't quit in TIMEOUT seconds, raise alarm
        signal.signal(signal.SIGALRM, self.timeoutHandler)
        signal.alarm(TIMEOUT)

        try:
            # TODO: Private function. We may want to fork the project for stability.
            out = self.venv._execute(cmdargs)
            print out
            ret = True

        except RuntimeError as e:
            LOG.info("Timed out waiting for app to finish. Exiting with success.")
            ret = True

        except Exception as e:
            LOG.exception("Exception while executing app in virtual env: %s", e.message)

        # Disable the alarm
        signal.alarm(0)
        return ret


def getVirtualEnvHandler():
    return VirtualEnvHandler()

def cleanupVirtualEnvHandler(venvHandler):
    shutil.rmtree(venvHandler.venvDir)

if __name__ == "__main__":
    venvHandler = VirtualEnvHandler()
    venvHandler.installReqsInVirtualEnv('')
    venvHandler.testAppInVirtualEnv()
    cleanupVirtualEnvHandler(venvHandler)
