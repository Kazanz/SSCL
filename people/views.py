from django.shortcuts import render, redirect, get_object_or_404

from people.forms import WaiverForm
from people.models import Waiver


def waiver(request):
    form = WaiverForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("thank-you")
    context = {'form': form}
    return render(request, 'waiver.html', context)


def thank_you(request):
    return render(request, 'thank_you.html', {})


def confirm(request, hash):
    return render(request, 'announcement.html', {'hash': hash})


def confirm_yes(request, hash):
    waiver = get_object_or_404(Waiver, hash=hash)
    waiver.confirm()
    return render(request, 'thank_you.html', {})


def confirm_no(request, hash):
    return render(request, 'thank_you_no.html', {})
