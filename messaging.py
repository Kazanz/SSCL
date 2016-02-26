from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from people.models import Waiver


def send_msg(request, subject, body):
    for waiver in Waiver.objects.all():
        if settings.DEBUG and "kazanski" not in waiver.email:
            continue
        waiver.re_hash()
        msg = make_msg(request, body, waiver.hash)
        sent = send_mail(subject, msg, settings.EMAIL_HOST_USER,
                         [waiver.email, waiver.number], fail_silently=False)
        if sent:
            waiver.sent = datetime.now()
            waiver.save()


def make_msg(request, body, hash):
    link = "{}/confirm/{}/".format(request.META['HTTP_HOST'], hash)
    formatter = body + "\n\n{}"
    text = formatter.format("Click this link to confirm: {}".format(link))
    return text
