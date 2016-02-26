from people.models import Waiver


def confirmed(request):
    return {'confirmed': Waiver.objects.filter(confirmed=True)}
