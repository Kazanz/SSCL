from people.models import Announcement, MessageTracker, Waiver
from sscl.stats import get_stats


def confirmed(request):
    data = {
        'confirmed': Waiver.objects.filter(confirmed=True),
        'announcement': Announcement.objects.get_or_create(title="main")[0],
        'tracker': MessageTracker.objects.order_by('-date').first(),
    }
    if "admin" in request.META['PATH_INFO']:
        data['stats'] = get_stats()
    return data
