from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from people.models import Waiver


DEBUG = settings.DEBUG
BASE_URL = settings.BASE_URL


@shared_task
def send_msg(subject, body):
    with open('celerylog.txt', 'a') as f:
        try:
            for waiver in Waiver.objects.all():
                if DEBUG and "kazanski" not in waiver.email:
                    continue

                hash = waiver.re_hash()

                if waiver.confirmed:
                    continue

                msg = make_msg(body, hash)
                try:
                    send_mail(subject, msg, settings.EMAIL_HOST_USER, [waiver.email, waiver.number], fail_silently=False)
                except:
                    continue
                else:
                    waiver.sent = datetime.now()
                    waiver.save()

                f.write("{} {} {} {}".format(hash, waiver.email, waiver.number, waiver.sent))
        except Exception as e:
		f.write(str(e))


def make_msg(body, hash):
    link = "{}/confirm/{}/".format(BASE_URL, hash)
    formatter = body + "\n\n{}"
    text = formatter.format("Click this link to confirm: {}".format(link))
    return text
