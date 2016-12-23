from rest_framework import serializers

from mystery_shopping.users.serializers import UserSerializer
from .models import DashboardTemplate
from .models import DashboardComment


class DashboardTemplateSerializer(serializers.ModelSerializer):
    """

    """

    users_repr = UserSerializer(source='users', many=True, read_only=True)

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


    def create(self, validated_data):
        users = validated_data.pop('users')
        instance = DashboardTemplate.objects.create(**validated_data)
        instance.users = users
        return instance

class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardComment
        fields = '__all__'
