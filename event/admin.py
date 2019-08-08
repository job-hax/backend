from django.contrib import admin
from .models import Event, EventType


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "host_user")
    list_filter = ("title", "event_date", "host_user")


admin.site.register(EventType)