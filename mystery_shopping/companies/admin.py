from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin

from mystery_shopping.companies.models import AdditionalInfoType
from .models import Industry, Company, Department, Entity, Section, SubIndustry, CompanyElement


@admin.register(Industry, SubIndustry, Company, Department, Entity, Section, AdditionalInfoType)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyElement)
class CompanyElementAdmin(MPTTModelAdmin, GuardedModelAdmin):
    list_display = ['element_name', 'element_type', 'tenant', 'additional_info', 'order']
