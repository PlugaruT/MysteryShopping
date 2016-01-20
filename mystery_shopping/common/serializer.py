from rest_framework import serializers

from .models import Country


class CountrySerializer(serializers.ModelSerializer):
    """
    Country serializer
    """
    class Meta:
        model = Country
