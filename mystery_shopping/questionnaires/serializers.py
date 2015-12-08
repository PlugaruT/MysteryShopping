from datetime import datetime

from rest_framework import serializers

from .models import QuestionnaireScript, QuestionnaireTemplate, QuestionnaireTemplateBlock, QuestionnaireTemplateQuestion
from mystery_shopping.mystery_shopping_utils.constants import Constants


class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    questionnaire_template = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplate.objects.all(), required=False)
    template_block = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplateBlock._default_manager.all(), required=False)

    # questionnaire_template =
    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'

    def single_multiple(self, to_validate):
        results = to_validate.split(Constants.CHOICES_SPLITTER)
        errors = []
        for result in results:
            answer_weight = result.split(Constants.CHOICE_BODY_VALUE_SPLITTER)
            if answer_weight[0] == '':
                errors.append("in answer '" + result + "' answer value is none")
            try:
                answer_weight[1]
                try:
                    int(answer_weight[1])
                except ValueError:
                    errors.append("in answer '" + result + "' the weight is not a number")
            except IndexError:
                errors.append("in answer '" + result + "' the weight does not exist")
        return errors

    def date_validator(self, to_validate):
        error = ''
        if len(to_validate) < 11:
            try:
                datetime.strptime(to_validate, Constants.DATE_VALIDATOR)
            except ValueError:
                error = 'the answer is not of date type'
        else:
            try:
                datetime.strptime(to_validate, Constants.DATETIME_VALIDATOR)
            except ValueError:
                error = 'the answer is not of datetime type'
        return error

    def validate_type(self, value):
        """
        Check if type of the question is an allowed one

        """
        if value[0] in ('s', 'm'):
            error = self.single_multiple(value[1:])
        elif value[0] == 't':
            error = self.date_validator(value[1:])
        else:
            raise serializers.ValidationError("Not a valid type")

        if error:
                raise serializers.ValidationError("Errors: {0}".format(error))
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
    template_block_questions = QuestionnaireTemplateQuestionSerializer(many=True)
    questionnaire_template = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireTemplate.objects.all(), required=False)
    lft = serializers.IntegerField(required=False)
    rght = serializers.IntegerField(required=False)
    tree_id = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = '__all__'

    def create(self, validated_data):
        # print(validated_data)
        children = validated_data.pop('children', None)
        template_block_questions = validated_data.pop('template_block_questions')

        template_block = QuestionnaireTemplateBlock.objects.create(**validated_data)

        for template_block_question in template_block_questions:
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


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """

    """
    template_blocks = QuestionnaireTemplateBlockSerializer(many=True, required=False)

    class Meta:
        model = QuestionnaireTemplate
        fields = ('title', 'template_blocks',)

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
