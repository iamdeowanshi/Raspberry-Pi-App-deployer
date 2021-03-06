import eventlet
import logging
from datetime import datetime
from datetime import timedelta

PERIODIC_TASK = None
LOG = logging.getLogger(__name__)


class Task(object):
    def __init__(self, func, interval):
        self.func = func
        self.interval = timedelta(seconds=interval)
        self.last_called = None

    def __eq__(self, other):
        if isinstance(other, Task):
            if other.func.__name__ == self.func.__name__:
                return True
        return False


class PeriodicTask(object):
    def __init__(self):
        self.task_list = []

    def run(self):
        while True:
            for task in self.task_list:
                if task.last_called is None or \
                        datetime.now() - task.last_called >= task.interval:
                    LOG.debug('Running task: %(task)s',
                            {'task': task.func.__name__})
                    eventlet.greenthread.spawn_n(task.func)
                    task.last_called = datetime.now()
            eventlet.greenthread.sleep(10)


def _get_object():
    global PERIODIC_TASK
    if not PERIODIC_TASK:
        PERIODIC_TASK = PeriodicTask()
    return PERIODIC_TASK


def add_task(function, interval, run_now=False, run_once=False):
    ptask = _get_object()
    task = Task(function, interval)
    if task not in ptask.task_list:
        if not run_once:
            ptask.task_list.append(task)
        if run_now:
            eventlet.greenthread.spawn_n(function)
            task.last_called = datetime.now()


def start():
    ptask = _get_object()
    eventlet.greenthread.spawn_n(ptask.run)
