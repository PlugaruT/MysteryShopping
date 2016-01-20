from rest_framework import serializers

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation


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

    def validate(self, data):
        # Check if number of maximum evaluations isn't surpassed
        if PlannedEvaluation.objects.filter(project=data['project']).count() >= Project.objects.get(pk=data['project'].id).research_methodology.number_of_evaluations:
            raise serializers.ValidationError('Number of evaluations is exceeded')
        else:
            return data


class AccomplishedEvaluationsSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = AccomplishedEvaluation
        fields = '__all__'
