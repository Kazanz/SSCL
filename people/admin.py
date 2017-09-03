from django.contrib import admin
from people.models import Waiver, MessageTracker

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
        'last_interaction',
    )


class MessageTrackerAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'views',
        'yes',
        'no',
    )
    actions = None
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def views(self, obj):
        waivers = Waiver.objects.filter(pk__in=obj.data['viewed']).all()
        return "<br>".join(sorted([waiver.full_name for waiver in waivers]))

    def yes(self, obj):
        waivers = Waiver.objects.filter(pk__in=obj.data['yes']).all()
        return "<br>".join(sorted([waiver.full_name for waiver in waivers]))

    def no(self, obj):
        waivers = Waiver.objects.filter(pk__in=obj.data['no']).all()
        return "<br>".join(sorted([waiver.full_name for waiver in waivers]))

    views.allow_tags = True
    yes.allow_tags = True
    no.allow_tags = True


admin.site.register(Waiver, WaiverAdmin)
admin.site.register(MessageTracker, MessageTrackerAdmin)
