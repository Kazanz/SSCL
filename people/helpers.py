from __future__ import unicode_literals

import random


def unique_hash(cls, field):
    for _ in range(100):
        v = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
        if not cls.objects.filter(**{field: v}).count():
            return v
    else:
        raise RuntimeError("Recursion depth exceeeded for hash")



def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d
