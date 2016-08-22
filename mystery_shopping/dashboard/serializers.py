from rest_framework import serializers

from .models import DashboardTemplate
from .models import DashboardComment


class DashboardTemplateSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardTemplate
        fields = '__all__'
        extra_kwargs = {
            'modified_by': {
                'required': False
            },
            'modified_date': {
                'required': False
            }
        }


class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardComment
        fields = '__all__'
