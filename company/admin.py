from django.contrib import admin

from utils.export_csv import ExportCsv
from .models import Company


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ('company', 'company_logo', 'cb_name',
                    'cb_company_logo', 'cb_domain', 'location_address')
    list_filter = ('company', 'company_logo', 'cb_name',
                    'cb_company_logo', 'cb_domain', 'location_address')
    actions = ["export_as_csv"]
