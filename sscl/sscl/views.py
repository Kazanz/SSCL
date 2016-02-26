from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404

from messaging import send_msg
from people.models import Waiver


@require_http_methods(['POST'])
@csrf_exempt
def send_emails(request):
    if request.user.is_authenticated():
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        if subject and body:
            send_msg(request, subject, body)
            return HttpResponse(200)
    return HttpResponse(400)


def confirm(request, hash):
    waiver = get_object_or_404(Waiver, hash=hash)
    waiver.confirm()
    return redirect('thank-you')
