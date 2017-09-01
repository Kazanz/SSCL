from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from people.forms import WaiverForm
from people.models import MessageTracker, Waiver


def waiver(request):
    waiver = Waiver.objects.filter(email=request.POST.get('email')).first()
    form = WaiverForm(request.POST or None, instance=waiver)
    if form.is_valid():
        form.save()
        return redirect("thank-you")
    context = {'form': form}
    return render(request, 'waiver.html', context)


def thank_you(request):
    return render(request, 'thank_you.html', {})


def confirm(request, hash):
    waiver = get_object_or_404(Waiver, hash=hash)
    MessageTracker.viewed(waiver)
    return render(request, 'announcement.html', {'hash': hash})


def msg(request):
    return render(request, 'announcement.html', {'hash': None})


def confirm_yes(request, hash):
    waiver = get_object_or_404(Waiver, hash=hash)
    waiver.confirm()
    MessageTracker.yes(waiver)
    return render(request, 'thank_you.html', {})


def confirm_no(request, hash):
    waiver = get_object_or_404(Waiver, hash=hash)
    MessageTracker.no(waiver)
    return render(request, 'thank_you_no.html', {})


def sending_email(request):
    if MessageTracker.objects.order_by('-date').first().is_sending_email:
        return HttpResponse("yes")
    return HttpResponse("no")


def sending_text(request):
    if MessageTracker.objects.order_by('-date').first().is_sending_text:
        return HttpResponse("yes")
    return HttpResponse("no")


def unlock(request):
    tracker = MessageTracker.objects.order_by('-date').first()
    tracker.sending_email = False
    tracker.sending_text = False
    tracker.save()
    return redirect('/admin/')
