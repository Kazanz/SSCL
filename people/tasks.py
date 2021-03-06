import unicodedata
from datetime import datetime
from time import sleep

import nexmo
import requests
from celery import shared_task
from django.conf import settings
from twilio.rest import Client

from people.models import Waiver, MessageTracker, SendHistory


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL
LINK_TEMPLATE_TAG = settings.LINK_TEMPLATE_TAG


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


def send_messages(subject, body=None, txtbody=None, withlink=True):
    send_all.delay(subject, body, txtbody, withlink)

@shared_task
def send_all(subject, body=None, txtbody=None, withlink=True):
    for waiver in Waiver.objects.all():
        try:
            send_msg(waiver, subject, body, txtbody, withlink)
        except:
            pass

#@shared_task
def send_msg(waiver, subject, body=None, txtbody=None, withlink=True):
    tracker = MessageTracker.objects.order_by('-date').first()
    if body:
        tracker.sending_email = True
    if txtbody:
        tracker.sending_text = True
    tracker.save()

    history = SendHistory.objects.create(tracker=tracker)

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

    tracker.sending_email = False
    tracker.sending_text = False
    tracker.save()

def make_msg(body, hash):
    link = "{}/confirm/{}/".format(BASE_URL, hash)
    body = unicodedata.normalize("NFKD", body).encode('ascii', 'ignore')

    try:
        body.index(LINK_TEMPLATE_TAG)
    except ValueError:
        return "{}\n{}".format(link, body)
    else:
        return body.replace(LINK_TEMPLATE_TAG, link)


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
        'from': '18134363052',
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


def send_with_twilio(number, msg, tracker):
    if settings.DEBUG:
        number = "8133893559"
    account_sid = '...'
    auth_token = "..."
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=msg,
        from_='+17272058646',
        to="+1" + number,
    )


def send_msg_sync(waiver, subject, body=None, txtbody=None, withlink=True):
    tracker = MessageTracker.objects.order_by('-date').first()
    if body:
        tracker.sending_email = True
    if txtbody:
        tracker.sending_text = True
    tracker.save()

    history = SendHistory.objects.create(tracker=tracker)

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

    tracker.sending_email = False
    tracker.sending_text = False
    tracker.save()

