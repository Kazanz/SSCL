from datetime import datetime
from time import sleep

import nexmo
import requests
from celery import shared_task
from django.conf import settings

from people.models import Waiver, MessageTracker, SendHistory


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


def catch_error(f, method, waiver, history, *args):
    try:
        f(*args)
    except:
        field = method + "_errors"
        error = getattr(history, field)
        error.append(waiver.full_name)
        setattr(history, field, error)
        history.save()
    else:
        field = method + "_success"
        success = getattr(history, field)
        success.append(waiver.full_name)
        setattr(history, field, success)
        history.save()


@shared_task
def send_msg(subject, body=None, txtbody=None, withlink=True):
    tracker = MessageTracker.objects.order_by('-date').first()
    if body:
        tracker.sending_email = True
    if txtbody:
        tracker.sending_text = True
    tracker.save()

    history = SendHistory.objects.create(tracker=tracker)

    for waiver in Waiver.objects.all():
        if body:
            msg = make_msg(body, waiver.hash) if withlink else body
            catch_error(send_with_mailgun, 'email', waiver, history,
                        waiver.email, subject, msg)
        if txtbody:
            textmsg = make_msg(txtbody, waiver.hash)
            catch_error(send_with_nexmo, 'txt', waiver, history,
                        waiver.phone, textmsg, tracker)
        waiver.sent = datetime.now()
        waiver.save()
        sleep(2)

    if body:
        tracker.sending_email = False
    if txtbody:
        tracker.sending_text = False
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


def send_with_nexmo(number, msg, tracker):
    if settings.DEBUG:
        number = "8133893559"
    client = nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)
    res = client.send_message({
        'from': '18552436932',
        'to': "1" + number,
        'text': msg
    })
    messages = res.get('messages', [])
    if len(messages):
        ids = tracker.nexmo_ids
        for msg in messages:
            msg_id = msg.get('message-id')
            if msg_id:
                ids.append(msg_id)
        tracker.nexmo_ids = ids
        tracker.save()
