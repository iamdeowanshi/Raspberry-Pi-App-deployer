import signal
import git
import logging

LOG = logging.getLogger(__name__)

TIMEOUT = 30

# TODO: Dedupe with alarm handler in VirtualEnv
def timeoutHandler(signum, frame):
    raise RuntimeError("Error")

def gitClone(cloneDir, gitURL):
    ret = False

    # If clone doesn't complete in TIMEOUT seconds, raise alarm.
    # TODO: This is in place to handle non-public/invalid github URLs, since
    # trying to clone those asks for user authentication. Use timeouts for
    # now to identify this condition.

    signal.signal(signal.SIGALRM, timeoutHandler)
    signal.alarm(TIMEOUT)

    try:
        repo = git.Repo.clone_from(gitURL, cloneDir)
        LOG.info("Successfully cloned repo.")
        ret = True
    except RuntimeError as e:
        LOG.error("Timed out waiting for clone to finish.")
    except Exception as e:
        LOG.exception("Exception while cloning repo: %s", gitURL)

    # Disable the alarm
    signal.alarm(0)

    return ret

if __name__ == "__main__":
    gitClone('/tmp/gitclonetest/ar-virtualenv-api', 'https://github.com/arteria/ar-virtualenv-api')
