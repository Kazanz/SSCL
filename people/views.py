from django.shortcuts import render, redirect

from people.forms import WaiverForm
from people.models import Announcement


def waiver(request):
    form = WaiverForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("thank-you")
    context = {'form': form}
    return render(request, 'waiver.html', context)


def thank_you(request):
    return render(request, 'thank_you.html', {})


def confirm(request):
    announcement = Announcement.objects.get(title="main")
    return render(request, 'announcement.html', {'announcement': announcement})
