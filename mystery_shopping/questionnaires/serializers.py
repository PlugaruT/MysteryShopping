from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import QuestionnaireScript, QuestionnaireTemplate, Questionnaire, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireQuestion



class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireTemplate
        fields = ('title', 'script', 'template_blocks',)


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'


class QuestionnaireTemplateBlockSerializer(serializers.ModelSerializer):
    """

    """
    children = RecursiveField('QuestionnaireTemplateBlockSerializer', required=False, many=True)  # Never touch again!
    template_block_questions = QuestionnaireTemplateQuestionSerializer(many=True)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = ('title', 'weight', 'parent_block', 'template_block_questions', 'children')
