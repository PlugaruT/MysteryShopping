from django.contrib import admin

from .models import Industry, Company, Department, Entity, Section, SubIndustry, CompanyElement


@admin.register(Industry, SubIndustry, Company, Department, Entity, Section, CompanyElement)
class CompanyAdmin(admin.ModelAdmin):
    pass
