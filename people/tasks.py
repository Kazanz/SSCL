from datetime import datetime
from time import sleep

import nexmo
import requests
from celery import shared_task
from django.conf import settings

from people.models import Waiver, MessageTracker


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


def catch_error(f, method, waiver, tracker, *args):
    try:
        f(*args)
    except:
        field = method + "_errors"
        error = getattr(tracker, field)
        error.append(waiver.full_name)
        setattr(tracker, field, error)
        tracker.save()
    else:
        field = method + "_success"
        success = getattr(tracker, field)
        success.append(waiver.full_name)
        setattr(tracker, field, success)
        tracker.save()


@shared_task
def send_msg(subject, body=None, txtbody=None, withlink=True):
    tracker = MessageTracker.objects.order_by('-date').first()
    tracker.sending = True
    tracker.save()

    for waiver in Waiver.objects.all():
        if body:
            msg = make_msg(body, waiver.hash) if withlink else body
            catch_error(send_with_mailgun, 'email', waiver, tracker,
                        waiver.email, subject, msg)
        if txtbody:
            textmsg = make_msg(txtbody, waiver.hash)
            catch_error(send_with_nexmo, 'txt', waiver, tracker,
                        waiver.phone, subject, textmsg)
        waiver.sent = datetime.now()
        waiver.save()
        sleep(.5)

    tracker.sending = False
    tracker.save()


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
    assert 0
    if settings.DEBUG:
        number = "8133893559"
    client = nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)
    client.send_message({
        'from': '12013508725',
        'to': "1" + number,
        'text': "{} - {}".format(subject, msg)
    })
