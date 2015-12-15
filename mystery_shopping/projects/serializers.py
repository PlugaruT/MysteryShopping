from rest_framework import serializers

from .models import Project, ResearchMethodology


class ProjectSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Project
        fields = '__all__'


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = ResearchMethodology

        fields = '__all__'
