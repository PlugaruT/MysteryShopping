from django.contrib import admin

from .models import Country, CountryRegion, County, City, Sector


@admin.register(Country, CountryRegion, County, City, Sector)
class RegionAdmin(admin.ModelAdmin):
    pass

