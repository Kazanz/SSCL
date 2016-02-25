from __future__ import unicode_literals

import hashlib
from random import SystemRandom


def unique_hash(cls, field):
    for _ in range(100):
        v = hashlib.sha1(str(SystemRandom().random()).encode()).hexdigest()
        if not cls.models.filter(**{field: v}).count():
            return v
    else:
        raise RuntimeError("Recursion depth exceeeded for hash")
