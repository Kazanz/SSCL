from people.models import Announcement, Waiver
from sscl.stats import get_stats


def confirmed(request):
    data = {
        'confirmed': Waiver.objects.filter(confirmed=True),
        'announcement': Announcement.objects.get_or_create(title="main")[0],
    }
    if "admin" in request.META['PATH_INFO']:
        data['stats'] = get_stats()
    return data
