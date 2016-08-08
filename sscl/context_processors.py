from people.models import Announcement, MessageTracker
from sscl.stats import msg_stats


def stats(request):
    context = {"announcement": Announcement.objects.first()}
    if "admin" not in request.META['PATH_INFO']:
        return context
    context.update(msg_stats())
    context['tracker'] = MessageTracker.objects.order_by('-date').first()
    context["filter_date"] = context['tracker'].date.strftime('%m/%d/%Y')
    return context
