from factory.django import DjangoModelFactory
from factory import fuzzy
from factory import SubFactory

from mystery_shopping.common.models import Country, CountryRegion, County, City, Sector


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country

    name = fuzzy.FuzzyText(length=15)


class CountryRegionFactory(DjangoModelFactory):
    class Meta:
        model = CountryRegion

    country = SubFactory(CountryFactory)
    name = fuzzy.FuzzyText(length=20)


class CountyFactory(DjangoModelFactory):
    class Meta:
        model = County

    country = SubFactory(CountryFactory)
    country_region = SubFactory(CountryRegionFactory)

    name = fuzzy.FuzzyText(length=20)


class CityFactory(DjangoModelFactory):
    class Meta:
        model = City

    county = SubFactory(CountyFactory)
    name = fuzzy.FuzzyText(length=10)
    zip_code = fuzzy.FuzzyText(length=5)


class SectorFactory(DjangoModelFactory):
    class Meta:
        model = Sector

    city = SubFactory(CityFactory)
    name = fuzzy.FuzzyText(length=10)
