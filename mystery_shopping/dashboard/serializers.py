from rest_framework import serializers

from .models import DashboardTemplate
from .models import DashboardComment


class DashboardTemplateSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardTemplate
        fields = '__all__'


class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardComment
        fields = '__all__'
