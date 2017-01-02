from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Industry, Company, Department, Entity, Section, SubIndustry, CompanyElement


@admin.register(Industry, SubIndustry, Company, Department, Entity, Section)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyElement)
class CompanyElementAdmin(MPTTModelAdmin):
    list_display = ['element_name', 'element_type', 'additional_info']
