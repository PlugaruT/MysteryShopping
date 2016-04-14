from json import dumps
from json import loads
from rest_framework import serializers

from .models import DashboardTemplate
from .models import DashboardComment


class DashboardTemplateSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardTemplate
        fields = '__all__'

    def validate_structure(self, value):
        # Check if value if of JSON type
        try:
            deserialized_value = loads(value)
        except ValueError:
            raise serializers.ValidationError('Not of JSON type')
        return value

    def create(self, validated_data):
        structure = validated_data.get('structure', [])
        validated_data['structure'] = ''
        dashboard = DashboardTemplate.objects.create(**validated_data)

        deserialized_structure = loads(structure)
        # Iterate through tiles and check whether it will have a comment or not
        for tile in deserialized_structure:
            if tile.get('show_comment', False):
                comment = DashboardComment.objects.create(dashboard=dashboard)
                tile['comment_source'] = comment.pk

        # Update dashboard structure with comment ids
        structure = dumps(deserialized_structure)
        dashboard.structure = structure
        dashboard.save()
        return dashboard


class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardComment
        fields = '__all__'
