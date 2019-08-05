from django.contrib import admin
from .models import Agreement, Country

# Register your models here.
@admin.register(Agreement)
class UserAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_html')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "code2", "code3")
    list_filter = ("name", "region", "code2", "code3")
