from rest_framework import serializers

from mystery_shopping.users.serializers import UserSerializer
from .models import DashboardTemplate
from .models import DashboardComment


class DashboardTemplateSerializer(serializers.ModelSerializer):
    """
    Default Dashboard Template serializer.
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

    def create(self, validated_data):
        users = validated_data.pop('users')
        instance = DashboardTemplate.objects.create(**validated_data)
        instance.users = users
        return instance


class DashboardTemplateSerializerGET(DashboardTemplateSerializer):
    """
    Nested Dashboard Template serializer.
    """
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = DashboardTemplate
        fields = '__all__'

class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = DashboardComment
        fields = '__all__'
