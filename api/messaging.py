import os
import random
import re

from flask import request, current_app
from flask_mail import Message


class Messenger(object):
    carriers = {
        "AT&T": "@txt.att.net",
        "T-Mobile": "@tmomail.net",
        "Cricket": "@sms.mycricket.com",
        "MetroPCS": "@mymetropcs.com",
        "Verizon": "@vtext.com",
        "Sprint": "@messaging.sprintpcs.com",
    }
    strip = lambda self, x: re.sub(r'\W+', '', x).lower()

    def __init__(self, mail, sheet):
        self.mail = mail
        self.sheet = sheet
        self.subject = None
        self.body = None

    def send(self):
        if self.subject and self.body:
            data = self.data_gen(self.sheet.get_field_values('Email'))
            for email, phone, hash in data:
                text, html = self.make_msg(self.body, hash)
                if current_app.config['DEBUG'] and "kazanski" not in email:
                    email = email + ".testing"
                    phone = phone + ".testing"
                    continue
                email_msg = Message(self.subject, recipients=[email])
                sms_msg = Message(self.subject, recipients=[phone])
                email_msg.body = sms_msg.body = text
                email_msg.html = html
                self.mail.send(email_msg)
                self.mail.send(sms_msg)

    def get_numbers(self):
        numbers = [self.strip(n) for n in self.sheet.get_field_values('Phone')]
        carriers = self.sheet.get_field_values('Phone Carrier')
        return [number + self.carrier_suffix(carrier)
                for number, carrier in zip(numbers, carriers)]

    def carrier_suffix(self, carrier):
        carrier = self.strip(carrier)
        for k, suffix in self.carriers.items():
            if re.match(carrier, self.strip(k)):
                return suffix
        return ''

    def make_msg(self, body, hash):
        link = "{}confirm/{}".format(request.url_root, hash)
        formatter = body + "\n\n{}"
        html_msg = '<a href="{}">Click here to confirm.</a>'.format(link)
        html = formatter.format(html_msg)
        text = formatter.format("Click this link to confirm: {}".format(link))
        return text, html

    def data_gen(self, emails):
        hash_suffixes = random.sample(range(100, 999), len(emails))
        numbers = self.get_numbers()
        for i, email in enumerate(emails):
            hash = os.urandom(2).encode('hex') + str(hash_suffixes[i])
            current_app.Player.update(email, hash=hash, confirmed=False)
            yield (email, numbers[i], hash)

    def strip(self, x):
        return re.sub(r'\W+', '', x).lower()
