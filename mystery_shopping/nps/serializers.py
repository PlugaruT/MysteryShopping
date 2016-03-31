from rest_framework import serializers

from .models import CodedCauseLabel
from .models import CodedCause
from mystery_shopping.questionnaires.models import QuestionnaireQuestion


class CodedCauseLabelSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCauseLabel
        fields = '__all__'


class CodedCauseSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CodedCause
        fields = '__all__'


class QuestionnaireQuestionToEncodeSerializer(serializers.ModelSerializer):
    """Serializes only the minimal required fields to be able to encode a question's answer
    for the Customer Experience Index indicators.
    """
    class Meta:
        model = QuestionnaireQuestion
        fields = ('answer', 'type', 'id')
        read_only_fields = ('answer', 'type', 'id')