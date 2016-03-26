from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404

from people.models import Waiver
from people.tasks import send_msg


@require_http_methods(['POST'])
@csrf_exempt
def send_emails(request):
    if request.user.is_authenticated():
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        if subject and body:
            send_msg.delay(subject, body)
            return HttpResponse(200)
    return HttpResponse(400)


def clear(request):
    Waiver.objects.all().update(confirmed=False)
    return redirect('/admin/')


def confirm(request, hash):
    waiver = Waiver.objects.filter(hash=hash).first()
    if waiver:
        waiver.confirm()
    return redirect('thank-you')
