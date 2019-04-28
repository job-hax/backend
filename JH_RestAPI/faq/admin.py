from django.contrib import admin
from .models import *
from django.utils.translation import gettext as _


class FaqItemInline(admin.TabularInline):
    model = Item
    extra = 0
    max_num = 15


class FaqAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published')
    inlines = [FaqItemInline,]

admin.site.register(Faq, FaqAdmin)
