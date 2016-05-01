import json

from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404

from people.models import Announcement, Waiver
from people.tasks import send_msg


@require_http_methods(['POST'])
@csrf_exempt
def send_emails(request):
    if request.user.is_authenticated():
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        withlink = request.POST.get("withlink")
        if subject and body and withlink:
            send_msg.delay(subject, body, withlink == "true")
            return HttpResponse(200)
    return HttpResponse(400)


def clear(request):
    Waiver.objects.all().update(confirmed=False)
    return redirect('/admin/')


@require_http_methods(['POST'])
def announcement(request):
    type_ = "error"
    msg = "An error occured!"
    if request.user.is_authenticated():
        text = request.POST.get("editor1")
        if text:
            announcement = Announcement.objects.get(title="main")
            announcement.text = text
            announcement.save()
            type_ = "success"
            msg = "Announcement successfully updated!"
    getattr(messages, type_)(request, msg)
    return redirect("/admin/")


@require_http_methods(['POST'])
@csrf_exempt
def image_update(request):
    waiver = get_object_or_404(Waiver, pk=int(request.POST.get('pk')))
    waiver.image = request.POST.get('image')
    waiver.save()
    return HttpResponse("Success!")


def waiver_data(request):
    return HttpResponse(json.dumps([
        {
            'pk': w.pk,
            'name': w.full_name,
            'confirmed': w.confirmed,
            'image': w.image
        } for w in Waiver.objects.all()
    ]))
