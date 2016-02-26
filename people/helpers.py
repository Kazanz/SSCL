from __future__ import unicode_literals

import random


def unique_hash(cls, field):
    for _ in range(100):
        v = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
        if not cls.objects.filter(**{field: v}).count():
            return v
    else:
        raise RuntimeError("Recursion depth exceeeded for hash")
