from django.contrib import admin
from people.models import Waiver

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
        'first',
        'last',
        'photo',
        'email',
        'phone',
        'carrier',
        'dob',
        'signature',
        'created',
        'confirmed',
        'sent',
    )


admin.site.register(Waiver, WaiverAdmin)
