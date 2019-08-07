from django.contrib import admin

from .models import *


class PollItemInline(admin.TabularInline):
    model = Item
    extra = 0
    max_num = 15


class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'vote_count', 'is_published')
    inlines = [PollItemInline, ]


admin.site.register(Poll, PollAdmin)


class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'ip', 'user', 'datetime')
    list_filter = ('poll', 'datetime')


admin.site.register(Vote, VoteAdmin)
