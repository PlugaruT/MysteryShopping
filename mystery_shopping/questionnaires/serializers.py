from rest_framework import serializers

from .models import QuestionnaireScript
from .models import Questionnaire
from .models import QuestionnaireTemplate
from .models import QuestionnaireBlock
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireQuestion
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireTemplateQuestionChoice
from .models import QuestionnaireQuestionChoice
from .validators import ValidateQuestion


class QuestionnaireTemplateQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """
    template_question = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplateQuestion.objects.all(), required=False)

    class Meta:
        model = QuestionnaireTemplateQuestionChoice
        fields = '__all__'


class QuestionnaireQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = QuestionnaireQuestionChoice
        fields = '__all__'


class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    """

    """
    questionnaire = serializers.PrimaryKeyRelatedField(queryset=Questionnaire.objects.all(), required=False)
    block = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireBlock._default_manager.all(), required=False)
    question_choices = QuestionnaireQuestionChoiceSerializer(many=True, required=False)

    class Meta:
        model = QuestionnaireQuestion
        fields = '__all__'

    # def validate_type(self, value):
    #     """
    #     Check if type of the question is an allowed one
    #
    #     """
    #     if value[0] in ('s', 'm'):
    #         validator = ValidateQuestion()
    #         error = validator.single_multiple(value[1:])
    #     elif value[0] == 't':
    #         validator = ValidateQuestion()
    #         error = validator.date_validator(value[1:])
    #     else:
    #         raise serializers.ValidationError("Not a valid type")
    #
    #     if error:
    #             raise serializers.ValidationError("Errors: {0}".format(error))
    #     return value

    def create(self, validated_data):
        question_choices = validated_data.pop('question_choices', None)

        question = QuestionnaireTemplateQuestion.objects.create(**validated_data)

        for question_choice in question_choices:
            question_choice['question'] = question.id
            question_choice_ser = QuestionnaireTemplateQuestionChoiceSerializer(data=question_choice)
            question_choice_ser.is_valid(raise_exception=True)
            question_choice_ser.save()
        return question

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    # questionnaire_template = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplate.objects.all(), required=False)
    # template_block = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplateBlock._default_manager.all(), required=False)
    template_question_choices = QuestionnaireTemplateQuestionChoiceSerializer(many=True, required=False)

    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'
        extra_kwargs = {'questionnaire_template': {'required': False},
                        'template_block': {'required': False}}

    # def validate_type(self, value):
    #     """
    #     Check if type of the question is an allowed one
    #
    #     """
    #     if value[0] in ('s', 'm'):
    #         validator = ValidateQuestion()
    #         error = validator.single_multiple(value[1:])
    #     elif value[0] == 't':
    #         validator = ValidateQuestion()
    #         error = validator.date_validator(value[1:])
    #     else:
    #         raise serializers.ValidationError("Not a valid type")
    #
    #     if error:
    #             raise serializers.ValidationError("Errors: {0}".format(error))
    #     return value

    def create(self, validated_data):
        template_question_choices = validated_data.pop('template_question_choices', None)

        template_question = QuestionnaireTemplateQuestion.objects.create(**validated_data)

        for template_question_choice in template_question_choices:
            template_question_choice['template_question'] = template_question.id
            template_question_choice_ser = QuestionnaireTemplateQuestionChoiceSerializer(data=template_question_choice)
            template_question_choice_ser.is_valid(raise_exception=True)
            template_question_choice_ser.save()
        return template_question

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class QuestionnaireBlockSerializer(serializers.ModelSerializer):
    """

    """
    block_questions = QuestionnaireQuestionSerializer(many=True)
    # questionnaire = serializers.PrimaryKeyRelatedField(queryset=Questionnaire.objects.all(), required=False)
    lft = serializers.IntegerField(required=False)
    rght = serializers.IntegerField(required=False)
    tree_id = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)

    class Meta:
        model = QuestionnaireBlock
        fields = '__all__'
        extra_kwargs = {'questionnaire': {'required': False}}

    def create(self, validated_data):
        # print(validated_data)
        children = validated_data.pop('children', None)
        block_questions = validated_data.pop('block_questions')

        block = QuestionnaireTemplateBlock.objects.create(**validated_data)

        for block_question in block_questions:
            # print(block_question)
            block_question['questionnaire_template'] = block.questionnaire_template.id
            block_question['block'] = block.id
            block_question_ser = QuestionnaireTemplateQuestionSerializer(data=block_question)
            block_question_ser.is_valid(raise_exception=True)
            block_question_ser.save()
        return block

    def update(self, instance, validated_data):
        print(validated_data)
        # instance.title = validated_data.get('title', instance.title)
        # instance.weight = validated_data.get('weight', instance.weight)
        # instance.questionnaire = validated_data.get('questionnaire', instance.questionnaire)
        # instance.parent_block = validated_data.get('parent_block', instance.parent_block)
        # instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class QuestionnaireTemplateBlockSerializer(serializers.ModelSerializer):
    """

    """
    template_questions = QuestionnaireTemplateQuestionSerializer(many=True)
    # questionnaire_template = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplate.objects.all(), required=False)
    lft = serializers.IntegerField(required=False)
    rght = serializers.IntegerField(required=False)
    tree_id = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = '__all__'
        extra_kwargs = {'questionnaire_template': {'required': False}}

    def create(self, validated_data):
        # print(validated_data)
        children = validated_data.pop('children', None)
        template_questions = validated_data.pop('template_questions')

        template_block = QuestionnaireTemplateBlock.objects.create(**validated_data)

        for template_block_question in template_questions:
            # print(template_block_question)
            template_block_question['questionnaire_template'] = template_block.questionnaire_template.id
            template_block_question['template_block'] = template_block.id
            template_block_question_ser = QuestionnaireTemplateQuestionSerializer(data=template_block_question)
            template_block_question_ser.is_valid(raise_exception=True)
            template_block_question_ser.save()
        return template_block

    def update(self, instance, validated_data):
        print(validated_data)
        instance.title = validated_data.get('title', instance.title)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.questionnaire_template = validated_data.get('questionnaire_template', instance.questionnaire_template)
        instance.parent_block = validated_data.get('parent_block', instance.parent_block)
        instance.save()
        return instance


class QuestionnaireSerializer(serializers.ModelSerializer):
    """

    """
    blocks = QuestionnaireTemplateBlockSerializer(many=True, required=False)

    class Meta:
        model = Questionnaire
        fields = '__all__'  #('title', 'blocks', 'template',)

    def create(self, validated_data):
        # print(validated_data)
        blocks = validated_data.pop('blocks', None)
        questionnaire = QuestionnaireTemplate.objects.create(**validated_data)
        previous_block = None
        parents_id = {}
        if blocks:
            for block in blocks:
                block['questionnaire'] = questionnaire.id
                if block['lft'] == 1:
                    parents_id['level_' + str(block['level'])] = None
                elif block['level'] > previous_block.level:
                    parents_id['level_' + str(block['level'])] = previous_block.id

                block['parent_block'] = parents_id['level_' + str(block['level'])]
                block_ser = QuestionnaireTemplateBlockSerializer(data=block)
                block_ser.is_valid(raise_exception=True)
                current_block = block_ser.save()
                previous_block = current_block
        return questionnaire


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """

    """
    template_blocks = QuestionnaireTemplateBlockSerializer(many=True, required=False)

    class Meta:
        model = QuestionnaireTemplate
        fields = '__all__'  # ('title', 'template_blocks',)

    def create(self, validated_data):
        # print(validated_data)
        template_blocks = validated_data.pop('template_blocks', None)
        questionnaire_template = QuestionnaireTemplate.objects.create(**validated_data)
        previous_template_block = None
        parents_id = {}
        if template_blocks:
            for template_block in template_blocks:
                template_block['questionnaire_template'] = questionnaire_template.id
                if template_block['lft'] == 1:
                    parents_id['level_' + str(template_block['level'])] = None
                elif template_block['level'] > previous_template_block.level:
                    parents_id['level_' + str(template_block['level'])] = previous_template_block.id

                template_block['parent_block'] = parents_id['level_' + str(template_block['level'])]
                template_block_ser = QuestionnaireTemplateBlockSerializer(data=template_block)
                template_block_ser.is_valid(raise_exception=True)
                current_block = template_block_ser.save()
                previous_template_block = current_block
        return questionnaire_template
