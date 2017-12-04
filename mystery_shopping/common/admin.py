from django.contrib import admin

from mystery_shopping.common.models import City, Country, CountryRegion, County, Sector, Tag


@admin.register(Country, CountryRegion, County, City, Sector)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
