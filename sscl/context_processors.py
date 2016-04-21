from people.models import Announcement, Waiver


def confirmed(request):
    return {
        'confirmed': Waiver.objects.filter(confirmed=True),
        'announcement': Announcement.objects.get_or_create(title="main")[0],
    }
