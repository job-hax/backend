from django.contrib import admin
from .models import Agreement

# Register your models here.
@admin.register(Agreement)
class UserAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_html')
