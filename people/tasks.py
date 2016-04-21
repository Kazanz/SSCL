from datetime import datetime

import requests
from celery import shared_task
from django.conf import settings

from people.models import Waiver


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


@shared_task
def send_msg(subject, body, withlink=True):
    for waiver in Waiver.objects.all():
        msg = make_msg(body, waiver.hash) if withlink else body
        send_with_mailgun(waiver.email, subject, msg)
        send_with_mailgun(waiver.number, subject, msg)
        waiver.sent = datetime.now()
        waiver.save()


def make_msg(body, hash):
    link = "confirm/{}/".format(BASE_URL, hash)
    return "{}\n{}".format(body, link)


def send_with_mailgun(to, subject, msg):
    requests.post(
        settings.MAIL_GUN_URL,
        auth=("api", settings.MAIL_GUN_API_KEY),
        data={"from": "Steve Richardson <mailgun@sscl.info>",
              "to": to,
              "subject": subject,
              "text": msg})
