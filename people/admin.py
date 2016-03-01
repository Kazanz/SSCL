from django.contrib import admin
from django.contrib.auth.models import User, Group
#from djcelery.models import Crontab, Interval, PeriodicTask, Task, Worker

from people.models import Waiver

#admin.site.unregister(User)
#admin.site.unregister(Group)
#admin.site.unregister(Crontab)
#admin.site.unregister(Interval)
#admin.site.unregister(PeriodicTask)
#admin.site.unregister(Task)
#admin.site.unregister(Worker)
#

class WaiverAdmin(admin.ModelAdmin):
    fields = (
        'first',
        'last',
        'email',
        'phone',
        'carrier',
        'dob',
        'signature',
    )

    list_display = (
        'confirmed',
        'sent',
        'first',
        'last',
        'email',
        'phone',
        'carrier',
        'dob',
        'signature',
        'created',
    )

admin.site.register(Waiver, WaiverAdmin)
