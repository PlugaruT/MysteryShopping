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
        fields = '__all__'


class CountryRegionSerializer(serializers.ModelSerializer):
    """
    Country Region Serializer.
    """
    class Meta:
        model = CountryRegion
        fields = '__all__'


class CountySerializer(serializers.ModelSerializer):
    """
    County Serializer.
    """
    class Meta:
        model = County
        fields = '__all__'


class SectorSerializer(serializers.ModelSerializer):
    """
    Sector Serializer.
    """
    class Meta:
        model = Sector
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    """
    City Serializer.
    """
    sectors = SectorSerializer(many=True, required=False)
    county = serializers.CharField(source='county.name', read_only=True)

    class Meta:
        model = City
        fields = '__all__'
