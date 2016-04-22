import calendar
from datetime import date
from datetime import timedelta

import requests
from django.conf import settings


def get_stats():
    url = "https://api.mailgun.net/v3/{}/stats/total".format(
        settings.MAIL_GUN_DOMAIN)
    res = requests.get(
        url, auth=("api", settings.MAIL_GUN_API_KEY),
        params={
            "event": ["delivered", "opened", "clicked"],
            "start": last_wednesday(),
            "end": today(),
        })
    data = res.json()
    data['start'] = data['start'][:-13]
    return data


def last_wednesday():
    today = date.today()
    offset = (today.weekday() - 2) % 7 or 7
    last_wednesday = today - timedelta(days=offset)
    return calendar.timegm(last_wednesday.timetuple())


def today():
    today = date.today()
    return calendar.timegm(today.timetuple())
