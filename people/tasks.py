from datetime import datetime

import nexmo
import requests
from celery import shared_task
from django.conf import settings

from people.models import Waiver


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


@shared_task
def send_msg(subject, body=None, txtbody=None, withlink=True):
    for waiver in Waiver.objects.all():
        if body:
            msg = make_msg(body, waiver.hash) if withlink else body
            send_with_mailgun(waiver.email, subject, msg)
        if txtbody:
            textmsg = make_msg(txtbody, waiver.hash)
            send_with_nexmo(waiver.phone, subject, textmsg)
        waiver.sent = datetime.now()
        waiver.save()


def make_msg(body, hash):
    link = "{}/confirm/{}/".format(BASE_URL, hash)
    return "{}\n{}".format(body, link)


def send_with_mailgun(to, subject, msg):
    requests.post(
        settings.MAIL_GUN_URL,
        auth=("api", settings.MAIL_GUN_API_KEY),
        data={"from": "Steve Richardson <mailgun@sscl.info>",
              "to": to,
              "subject": subject,
              "text": msg})


def send_with_nexmo(number, subject, msg):
    if settings.DEBUG:
        number = "8133893559"
    client = nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)
    client.send_message({
        'from': '12013508725',
        'to': "1" + number,
        'text': "{} - {}".format(subject, msg)
    })
