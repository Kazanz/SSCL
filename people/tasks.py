from datetime import datetime

import requests
from celery import shared_task
from django.conf import settings

from people.models import Waiver


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


@shared_task
def send_msg(subject, body):
    for waiver in Waiver.objects.all():
        msg = make_msg(body, waiver.hash)
        send_with_mailgun(waiver.email, subject, msg)
        send_with_mailgun(waiver.number, subject, msg)
        waiver.sent = datetime.now()
        waiver.save()


def make_msg(body, hash):
    link = "{}/confirm/{}/".format(BASE_URL, hash)
    formatter = body + "\n\n{}"
    text = formatter.format("Click this link to confirm: {}".format(link))
    return text


def send_with_mailgun(to, subject, msg):
    requests.post(
        settings.MAIL_GUN_URL,
        auth=("api", settings.MAIL_GUN_API_KEY),
        data={"from": "Mailgun Sandbox <postmaster@sandboxd4e1c9825e0843e4b8a071d295448de7.mailgun.org>",
              "to": to,
              "subject": subject,
              "text": msg})
