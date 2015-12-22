from rest_framework import serializers

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = ResearchMethodology

        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = Project
        fields = '__all__'


class PlannedEvaluationSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = PlannedEvaluation
        fields = '__all__'



    def validate(self, attrs):
        if PlannedEvaluation.objects.filter(project=attrs['project']).count() >= self.project.research_methodology.number_of_evaluations:
            raise serializers.ValidationError('Number of evaluations is exceeded')
        else:
            return attrs
