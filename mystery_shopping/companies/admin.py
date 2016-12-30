from django.contrib import admin

from mystery_shopping.companies.models import CompanyElement
from .models import Industry, Company, Department, Entity, Section, SubIndustry


@admin.register(Industry, SubIndustry, Company, Department, Entity, Section, CompanyElement)
class CompanyAdmin(admin.ModelAdmin):
    pass
