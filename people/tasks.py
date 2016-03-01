import pytz
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from people.models import Waiver


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


@shared_task
def send_msg(subject, body):
    for waiver in Waiver.objects.all():
        if DEBUG and "kazanski" not in waiver.email:
            continue
        if waiver.sent and waiver.sent > pytz.utc.localize(datetime.utcnow() - timedelta(days=6)):
            continue
        #waiver.re_hash()
        msg = make_msg(body, waiver.hash)
        try:
            sent = send_mail(subject, msg, settings.EMAIL_HOST_USER,
                             ['kazanski.zachary@gmail.com', '8133893559@tmomail.net'], fail_silently=False)
        # Rather catch all errors and send out most emails than have it break.
        # Otherwise don't do this.
        except:
            continue
        else:
            if sent:
		pass
                #waiver.sent = datetime.now()
                #waiver.save()


def make_msg(body, hash):
    link = "{}/confirm/{}/".format(BASE_URL, hash)
    formatter = body + "\n\n{}"
    text = formatter.format("Click this link to confirm: {}".format(link))
    return text
