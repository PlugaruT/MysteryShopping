from rest_framework import serializers

from .models import Country
from .models import CountryRegion
from .models import County
from .models import City
from .models import Sector


class CountrySerializer(serializers.ModelSerializer):
    """
    Country serializer.
    """
    class Meta:
        model = Country


class CountryRegionSerializer(serializers.ModelSerializer):
    """
    Country Region Serializer.
    """
    class Meta:
        model = CountryRegion


class CountySerializer(serializers.ModelSerializer):
    """
    County Serializer.
    """
    class Meta:
        model = County


class CitySerializer(serializers.ModelSerializer):
    """
    City Serializer.
    """
    class Meta:
        model = City


class SectorSerializer(serializers.ModelSerializer):
    """
    Sector Serializer.
    """
    class Meta:
        model = Sector
