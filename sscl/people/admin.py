from django.contrib import admin
from django.contrib.auth.models import User, Group

from people.models import Waiver

admin.site.unregister(User)
admin.site.unregister(Group)

class WaiverAdmin(admin.ModelAdmin):
    list_display = (
        'confirmed',
        'first',
        'last',
        'email',
        'phone',
        'carrier',
        'dob',
        'signature',
        'football',
    )

admin.site.register(Waiver, WaiverAdmin)
