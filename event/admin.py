from django.contrib import admin
from .models import Event, EventType


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date_start", "event_date_end", "host_user")
    list_filter = ("title", "event_date_start", "event_date_end", "host_user")


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('id', 'name')
