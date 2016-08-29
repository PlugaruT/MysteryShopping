from django.contrib import admin

from .models import Industry, Company, Department, Entity, Section, SubIndustry


@admin.register(Industry, SubIndustry, Company, Department, Entity, Section)
class CompanyAdmin(admin.ModelAdmin):
    pass
