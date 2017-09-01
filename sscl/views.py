import json
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, get_object_or_404, render

from people.models import Announcement, MessageTracker, Waiver
from people.tasks import send_msg


@require_http_methods(['POST'])
@csrf_exempt
def send_emails(request):
    if request.user.is_authenticated():
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        txtbody = request.POST.get("txtbody")
        withlink = request.POST.get("withlink")
        if withlink and ((body and subject) or txtbody):
            send_msg.delay(subject, body, txtbody, withlink == "true")
            messages.success(request, "Your messages are being sent.")
            return HttpResponse(200)
        messages.error(request, "An error occured, please try again.")
    return HttpResponse(400)


def clear(request):
    Waiver.objects.all().update(confirmed=False)
    tracker = MessageTracker.objects.order_by('-date').first()
    if not tracker or tracker.has_data:
        MessageTracker.objects.create()
    elif tracker:
        tracker.date = datetime.now()
        tracker.save()
    return redirect('/admin/')


def callback(request):
    with open("delete.txt", "a") as f:
        f.write(json.dumps(request.GET))
        f.write("DONE")
    return HttpResponse(request.path)


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
            'view': w.confirmed,
            'image': w.image
        } for w in sorted(
            Waiver.objects.order_by('first'), key=lambda x: x.full_name
        )
    ]))

def tracker_data(request):
    tracker = MessageTracker.objects.order_by('-pk').first()
    return HttpResponse(json.dumps(
        {
            'pk': tracker.pk,
            'yes': tracker.yes_names,
            'no': tracker.no_names,
            'viewed': tracker.view_names,
        }
    ))


def history(request):
    trackers = MessageTracker.objects.order_by('-date').all()
    return render(request, 'admin/history.html', {'trackers': trackers})
