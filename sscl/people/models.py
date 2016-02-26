from __future__ import unicode_literals

import re

from django.db import models

from people.helpers import unique_hash


class Waiver(models.Model):
    CARRIERS = (
        ("@txt.att.net", "AT&T"),
        ("@tmomail.net", "T-Mobile"),
        ("@sms.mycricket.com", "Cricket"),
        ("@mymetropcs.com", "MetroPCS"),
        ("@vtext.com", "Verizon"),
        ("@messaging.sprintpcs.com", "Sprint"),
    )

    created = models.DateTimeField(auto_now_add=True)
    first = models.CharField(max_length=40)
    last = models.CharField(max_length=40)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=16)
    carrier = models.CharField(max_length=40, choices=CARRIERS)
    dob = models.DateField()
    football = models.BooleanField(default=False)
    signature = models.CharField(max_length=40)
    confirmed = models.BooleanField(default=False, blank=True)
    sent = models.DateTimeField(blank=True, null=True)
    hash = models.CharField(max_length=8, blank=True, null=True)

    def __unicode__(self):
        return self.first + " " + self.last

    def save(self, *args, **kwargs):
        self.phone = re.sub("\D", "", self.phone)
        super(Waiver, self).save(*args, **kwargs)

    def re_hash(self):
        self.hash = unique_hash(Waiver, 'hash')
        self.confirmed = False

    def confirm(self):
        self.hash = None
        self.confirmed = True
        self.save()

    @property
    def number(self):
        return self.phone + self.carrier
