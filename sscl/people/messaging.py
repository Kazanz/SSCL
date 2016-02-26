import re

from django.core.mail import send_mail

from people.models import Waiver


class Messenger(object):
    strip = lambda self, x: re.sub(r'\W+', '', x).lower()

    def __init__(self, subject, body):
        self.subject = subject
        self.body = body

    def send_all(self):
        if self.subject and self.body:
            data = self.data_generator()
            for email, phone, hash in data:
                text, html = self.make_msg(self.body, hash)
                if settings.DEBUG and "kazanski" not in email:
                    continue
                send_mail(self.subject, self.body, settings.EMAIL_USER,
                          [email, phone], fail_silently=False)

    def data_generator(self):
        waivers = Waiver.objects.all()
        for waiver in waivers:
            waiver.re_hash()
            yield waiver.email, waiver.number, waiver.hash

    def get_numbers(self):
        return [v['phone'] + v['carrier']
                for v in Waiver.objects.values("phone", "carrier")]

    def get_emails(self):
        return

    def make_msg(self, body, hash):
        link = "{}/api/confirm/{}".format(request.url_root, hash)
        formatter = body + "\n\n{}"
        html_msg = '<a href="{}">Click here to confirm.</a>'.format(link)
        html = formatter.format(html_msg)
        text = formatter.format("Click this link to confirm: {}".format(link))
        return text, html

    def strip(self, x):
        return re.sub(r'\W+', '', x).lower()
