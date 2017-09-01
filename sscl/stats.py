import requests
from datetime import datetime

import nexmo
from django.conf import settings
from memoize import memoize

from people.models import MessageTracker


@memoize(timeout=60)
def msg_stats():
    context = {}
    context['email_totals'] = email_total_stats()
    context['text_stats'] = {} #text_stats()
    return context


def email_total_stats():
    date = MessageTracker.objects.order_by('-date').first().date
    start = date.strftime('%s')
    totals = requests.get(
        settings.MAIL_GUN_TOTAL_STATS_URL,
        auth=("api", settings.MAIL_GUN_API_KEY),
        params={
            "event": ["accepted", "delivered", "failed"],
            "start": start,
            "end": datetime.now().strftime('%s')}
    ).json()
    totals.get('stats', []).reverse()
    return totals.get('stats', [])


def text_stats():
    client = nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)
    ids = MessageTracker.objects.order_by('-date').first().nexmo_ids
    stats = []
    for msg_id in ids:
        stat = client.get_message(msg_id)
        stat['date'] = stat['date-received']
        stats.append(stat)
    return stats
