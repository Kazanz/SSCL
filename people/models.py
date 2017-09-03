from __future__ import unicode_literals

import json
import re

from django.conf import settings
from django.db import models
from jsonfield import JSONField

from people.helpers import get_celery_worker_status, unique_hash


class Announcement(models.Model):
    title = models.CharField(max_length=255, default="main", unique=True)
    text = models.TextField()

    def __unicode__(self):
        return self.title


class MessageTracker(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    data = JSONField(default={"viewed": [], "yes": [], "no": []})
    nexmo_ids = JSONField(default=[])
    sending_email = models.BooleanField(default=False)
    sending_text = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Message Confirmation'
        verbose_name_plural = 'Message Confirmations'

    def __unicode__(self):
        return str(self.date)

    @property
    def is_sending_email(self):
        return self.sending_email and not get_celery_worker_status().get('ERROR')

    @property
    def is_sending_text(self):
        return self.sending_text and not get_celery_worker_status().get('ERROR')

    @property
    def yes_names(self):
        return sorted(self._names("yes"))

    @property
    def no_names(self):
        return sorted(self._names("no"))

    @property
    def view_names(self):
        return sorted(self._names("viewed"))

    def _names(self, field):
        data = []
        for pk in self.data[field]:
            waiver = Waiver.objects.filter(pk=pk).first()
            if waiver:
                data.append(waiver.full_name)
        return data

    @property
    def view_count(self):
        return len(self.data['viewed'])

    @property
    def yes_count(self):
        return len(self.data['yes'])

    @property
    def no_count(self):
        return len(self.data['no'])

    @property
    def has_data(self):
        return self.data['viewed'] or self.data['yes'] or self.data['no']

    @staticmethod
    def current_tracker():
        return MessageTracker.objects.latest('date')

    @staticmethod
    def viewed(waiver):
        tracker = MessageTracker.current_tracker()
        if waiver and waiver.pk not in tracker.data['viewed']:
            MessageTracker.add_to_data('viewed', waiver, tracker)

    @staticmethod
    def yes(waiver):
        tracker = MessageTracker.current_tracker()
        if waiver and waiver.pk not in tracker.data['yes']:
            MessageTracker.add_to_data('yes', waiver, tracker)

    @staticmethod
    def no(waiver):
        tracker = MessageTracker.current_tracker()
        if waiver and waiver.pk not in tracker.data['no']:
            MessageTracker.add_to_data('no', waiver, tracker)

    @staticmethod
    def add_to_data(key, waiver, tracker):
        data = tracker.data
        data_list = data[key]
        data_list.append(waiver.pk)
        data[key] = data_list
        tracker.data = data
        tracker.save()
        waiver.last_interaction = datetime.now()
        waiver.save()


class SendHistory(models.Model):
    tracker = models.ForeignKey(MessageTracker)
    email_success = JSONField(default=[])
    email_errors = JSONField(default=[])
    txt_success = JSONField(default=[])
    txt_errors = JSONField(default=[])


class Waiver(models.Model):
    CARRIERS = (
        ("@sms.3rivers.net", "3 River Wireless"),
        ("@paging.acswireless.com", "ACS Wireless"),
        ("@txt.att.net", "AT&T"),
        ("@message.alltel.com", "Alltel"),
        ("@bplmobile.com", "BPL Mobile"),
        ("@bellmobility.ca", "Bell Canada"),
        ("@txt.bellmobility.ca", "Bell Mobility"),
        ("@txt.bell.ca", "Bell Mobility (Canada)"),
        ("@blueskyfrog.com", "Blue Sky Frog"),
        ("@sms.bluecell.com", "Bluegrass Cellular"),
        ("@myboostmobile.com", "Boost Mobile"),
        ("er@cwwsms.com", "Carolina West Wireless"),
        ("@mobile.celloneusa.com", "Cellular One"),
        ("@csouth1.com", "Cellular South"),
        ("@cwemail.com", "Centennial Wireless"),
        ("@messaging.centurytel.net", "CenturyTel"),
        ("@txt.att.net", "Cingular (Now AT&T)"),
        ("@msg.clearnet.com", "Clearnet"),
        ("@comcastpcs.textmsg.com", "Comcast"),
        ("@corrwireless.net", "Corr Wireless Communications"),
        ("@sms.mycricket.com", "Cricket"),
        ("@mobile.dobson.net", "Dobson"),
        ("@sms.edgewireless.com", "Edge Wireless"),
        ("@fido.ca", "Fido"),
        ("@sms.goldentele.com", "Golden Telecom"),
        ("@msg.fi.google.com", "Google fi"),
        ("@messaging.sprintpcs.com", "Helio"),
        ("@text.houstoncellular.net", "Houston Cellular"),
        ("@ideacellular.net", "Idea Cellular"),
        ("@ivctext.com", "Illinois Valley Cellular"),
        ("@inlandlink.com", "Inland Cellular Telephone"),
        ("@pagemci.com", "MCI"),
        ("@text.mtsmobility.com", "MTS"),
        ("@mymetropcs.com", "Metro PCS"),
        ("@page.metrocall.com", "Metrocall"),
        ("@my2way.com", "Metrocall 2-way"),
        ("@fido.ca", "Microcell"),
        ("@clearlydigital.com", "Midwest Wireless"),
        ("@mobilecomm.net", "Mobilcomm"),
        ("@messaging.nextel.com", "Nextel"),
        ("@onlinebeep.net", "OnlineBeep"),
        ("@pcsone.net", "PCS One"),
        ("@txt.bell.ca", "President's Choice"),
        ("@sms.pscel.com", "Public Service Cellular"),
        ("@qwestmp.com", "Qwest"),
        ("@pcs.rogers.com", "Rogers AT&T Wireless"),
        ("@pcs.rogers.com", "Rogers Canada"),
        ("@txt.bell.ca", "Solo Mobile"),
        ("@email.swbw.com", "Southwestern Bell"),
        ("@messaging.sprintpcs.com", "Sprint"),
        ("@tms.suncom.com", "Sumcom"),
        ("@mobile.surewest.com", "Surewest Communicaitons"),
        ("@tmomail.net", "T-Mobile"),
        ("@msg.telus.com", "Telus"),
        ("@txt.att.net", "Tracfone"),
        ("@tms.suncom.com", "Triton"),
        ("@email.uscc.net", "US Cellular"),
        ("@uswestdatamail.com", "US West"),
        ("@utext.com", "Unicel"),
        ("@vtext.com", "Verizon"),
        ("@vmobl.com", "Virgin Mobile"),
        ("@vmobile.ca", "Virgin Mobile Canada"),
        ("@sms.wcc.net", "West Central Wireless"),
        ("@cellularonewest.com", "Western Wireless"),
    )

    image = models.CharField(max_length=999999, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    first = models.CharField(max_length=40)
    last = models.CharField(max_length=40)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=16)
    carrier = models.CharField(max_length=40, choices=CARRIERS)
    dob = models.DateField()
    signature = models.CharField(max_length=40)
    confirmed = models.BooleanField(default=False, blank=True)
    sent = models.DateTimeField(blank=True, null=True)
    hash = models.CharField(max_length=8, blank=True, null=True)
    last_interaction = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.first + " " + self.last

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = unique_hash(Waiver, 'hash')
        self.phone = re.sub("\D", "", self.phone)
        if self.pk is None:
            self.send_new_waiver_email()
        super(Waiver, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return "{} {}".format(self.first, self.last).title()

    def confirm(self):
        self.confirmed = True
        self.save()

    def cancel(self):
        self.confirmed = False
        self.save()

    @property
    def number(self):
        return self.phone + self.carrier

    def send_new_waiver_email(self):
        from people.tasks import send_with_mailgun
        to = "kazanski.zachary@gmail.com" if settings.DEBUG else "srichardson@streamsound.com"
        send_with_mailgun(to, "New Waiver: {} {}".format(self.first, self.last),
                          self.make_msg())

    def make_msg(self):
        fields = ('first', 'last', 'email', 'phone', 'carrier', 'dob')
        return "\n".join(["{}: {}".format(k, getattr(self, k))
                          for k in fields])

    def photo(self):
        if self.image:
            return '<img height="40"' \
                   'onMouseOver="this.style.height=\'175px\'"' \
                   'onMouseOut="this.style.height=\'40px\'"' \
                   'src="data:image/png;base64,{}"/>'.format(self.image)
    photo.allow_tags = True

    @property
    def _last_interaction_from_message_tracker(self):
        for m in MessageTracker.objects.order_by('-date').all():
            waiver_pks = reduce(lambda x, y: x + y, m.data.values())
            if self.pk in waiver_pks:
                return m.date


class ReceivedText(models.Model):
    waiver = models.ForeignKey(Waiver)
    text = models.CharField(max_length=255)

    @classmethod
    def create(cls, sms):
        phone = sms['msisdn'][1:] # Strip the leading +1 country code.
        waiver = Waiver.objects.filter(phone=phone).first()
        if waiver:
            instance = cls.objects.create(waiver=waiver, text=sms['text'])
