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


class SectorSerializer(serializers.ModelSerializer):
    """
    Sector Serializer.
    """
    class Meta:
        model = Sector


class CitySerializer(serializers.ModelSerializer):
    """
    City Serializer.
    """
    sectors = SectorSerializer(many=True, required=False)
    county = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = City
