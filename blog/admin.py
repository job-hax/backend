from django.contrib import admin

from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('publisher_profile', 'title', 'view_count',
                    'created_at', 'updated_at', 'is_publish', 'is_approved')
    list_filter = ('publisher_profile', 'title', 'view_count',
                    'created_at', 'updated_at', 'is_publish', 'is_approved')
