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

    def update(self, instance, validated_data):
        structure = validated_data.get('structure', [])

        comment_set = set()
        deserialized_structure = loads(structure)
        for tile in deserialized_structure:
            comment_set.add(tile.get('comment_source', None))
            if tile.get('show_comment', False):
                if tile.get('comment_source', None) is None:
                    comment = DashboardComment.objects.create(dashboard=instance)
                    tile['comment_source'] = comment.pk

        try:
            comment_set.remove(None)
        except KeyError:
            pass

        # Delete all comments whose tiles have been removed
        for comment in instance.dashboard_comments.all():
            if comment.id not in comment_set:
                comment.delete()

        structure = dumps(deserialized_structure)
        instance.structure = structure
        instance.save()
        return instance


class DashboardCommentSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = DashboardComment
        fields = '__all__'
