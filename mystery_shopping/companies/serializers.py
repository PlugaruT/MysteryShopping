from rest_framework import serializers

from .models import Industry, Company, Department, Section


class IndustrySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Industry
        fields = ('id', 'name')


class CompanySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Company
        fields = ('id', 'name')


class DepartmentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Department
        fields = ('id', 'name')


class SectionSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Section
        fields = ('id', 'name')

