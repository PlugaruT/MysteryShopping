from django.contrib import admin

from .models import Industry, Company, Department, Entity, Section


@admin.register(Industry, Company, Department, Entity, Section)
class CompanyAdmin(admin.ModelAdmin):
    pass
