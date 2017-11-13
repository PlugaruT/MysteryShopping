from django.contrib import admin

from mystery_shopping.common.models import Tag
from .models import Country, CountryRegion, County, City, Sector


@admin.register(Country, CountryRegion, County, City, Sector)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
