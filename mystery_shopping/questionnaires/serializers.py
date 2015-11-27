from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import QuestionnaireScript, QuestionnaireTemplate, QuestionnaireTemplateBlock, QuestionnaireTemplateQuestion


class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'

    def validate_type(self, value):
        """
        Check if type of the question is an allowed one

        """
        if value[0] == 's':
            raise serializers.ValidationError("Value is 's'")
        return value

    def create(self, validated_data):
        return QuestionnaireTemplateQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.question_body = validated_data.get('question_body', instance.question_body)
        instance.type = validated_data.get('type', instance.type)
        instance.show_comment = validated_data.get('show_comment', instance.show_comment)
        instance.max_score = validated_data.get('max_score', instance.max_score)
        instance.questionnaire_template = validated_data.get('questionnaire_template', instance.questionnaire_template)
        instance.template_block = validated_data.get('template_block', instance.template_block)
        instance.save()
        return instance


class QuestionnaireTemplateBlockSerializer(serializers.ModelSerializer):
    """

    """
    children = RecursiveField('QuestionnaireTemplateBlockSerializer', required=False, many=True)  # Never touch again!
    template_block_questions = QuestionnaireTemplateQuestionSerializer(many=True)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('children')
        validated_data.pop('template_block_questions')
        return QuestionnaireTemplateBlock.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print(validated_data)
        instance.title = validated_data.get('title', instance.title)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.questionnaire_template = validated_data.get('questionnaire_template', instance.questionnaire_template)
        instance.parent_block = validated_data.get('parent_block', instance.parent_block)
        instance.save()
        return instance


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """

    """
    template_blocks = QuestionnaireTemplateBlockSerializer(many=True)

    class Meta:
        model = QuestionnaireTemplate
        fields = ('title', 'script', 'template_blocks',)

    def create(self, validated_data):
        print(validated_data)
