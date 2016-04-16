from collections import OrderedDict

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
from .models import CrossIndexTemplate
from .models import CrossIndex


class QuestionnaireTemplateQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = QuestionnaireTemplateQuestionChoice
        fields = '__all__'
        extra_kwargs = {'template_question': {'required': False}}


class QuestionnaireQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = QuestionnaireQuestionChoice
        fields = '__all__'
        extra_kwargs = {'question': {'required': False}}


class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    """

    """
    question_choices = QuestionnaireQuestionChoiceSerializer(many=True, required=False)
    question_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireQuestion
        fields = '__all__'
        extra_kwargs = {'block': {'required': False},
                        'questionnaire': {'required': False},
                        'answer_choices': {'required': False, 'allow_empty': True}}

    def create(self, validated_data):
        question_choices = validated_data.pop('question_choices', None)

        question = QuestionnaireQuestion.objects.create(**validated_data)

        for question_choice in question_choices:
            question_choice['question'] = question.id
            question_choice_ser = QuestionnaireQuestionChoiceSerializer(data=question_choice)
            question_choice_ser.is_valid(raise_exception=True)
            question_choice_ser.save()
        return question

    def update(self, instance, validated_data):

        # instance.prepare_to_update()
        validated_data.pop('question_choices', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    template_question_choices = QuestionnaireTemplateQuestionChoiceSerializer(many=True, required=False)
    # this field will contain information that is needed to update a Questionnaire Template
    siblings = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'
        extra_kwargs = {'questionnaire_template': {'required': False},
                        'template_block': {'required': False}}

    def create(self, validated_data):
        if validated_data['questionnaire_template'].is_editable:
            template_question_choices = validated_data.pop('template_question_choices', [])
            siblings_to_update = validated_data.pop('siblings', [])
            for sibling in siblings_to_update:
                question_id = sibling.pop('question_id', None)
                # Check if the questions are from the same questionnaire template block
                question_to_update = QuestionnaireTemplateQuestion.objects.filter(pk=question_id, template_block=validated_data['template_block']).first()

                if question_to_update is not None:
                    for attr, value in sibling['question_changes'].items():
                        setattr(question_to_update, attr, value)
                    question_to_update.save()

            template_question = QuestionnaireTemplateQuestion.objects.create(**validated_data)

            for template_question_choice in template_question_choices:
                template_question_choice['template_question'] = template_question.id
                template_question_choice_ser = QuestionnaireTemplateQuestionChoiceSerializer(data=template_question_choice)
                template_question_choice_ser.is_valid(raise_exception=True)
                template_question_choice_ser.save()

            return template_question
        raise serializers.ValidationError('The Questionnaire Template this Question belongs to is not editable')

    def update(self, instance, validated_data):
        if instance.questionnaire_template.is_editable:
            # Delete all template question choices
            instance.prepare_to_update()
            template_question_choices = validated_data.pop('template_question_choices', [])
            # Create the 'new' template question choices
            for template_question_choice in template_question_choices:
                template_question_choice['template_question'] = instance.id
                template_question_choice_ser = QuestionnaireTemplateQuestionChoiceSerializer(
                    data=template_question_choice)
                template_question_choice_ser.is_valid(raise_exception=True)
                template_question_choice_ser.save()

            siblings_to_update = validated_data.pop('siblings', [])
            for sibling in siblings_to_update:
                question_id = sibling.pop('question_id')
                # Check if the questions are from the same questionnaire template block
                question_to_update = QuestionnaireTemplateQuestion.objects.filter(pk=question_id, template_block=validated_data['template_block']).first()

                if question_to_update is not None:
                    for attr, value in sibling['question_changes'].items():
                        setattr(question_to_update, attr, value)
                    question_to_update.save()

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class QuestionnaireBlockSerializer(serializers.ModelSerializer):
    """

    """
    questions = QuestionnaireQuestionSerializer(many=True)
    parent_order_number = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    order_number = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireBlock
        fields = '__all__'
        extra_kwargs = {'questionnaire': {'required': False},
                        'score': {'required': False}}

    def create(self, validated_data):
        # print(validated_data)
        children = validated_data.pop('children', None)
        questions = validated_data.pop('questions')

        block = QuestionnaireBlock.objects.create(**validated_data)

        for question in questions:
            # print(question)
            question['questionnaire'] = block.questionnaire.id
            question['block'] = block.id
            block_question_ser = QuestionnaireQuestionSerializer(data=question)
            block_question_ser.is_valid(raise_exception=True)
            block_question_ser.save()
        return block

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class QuestionnaireTemplateBlockSerializer(serializers.ModelSerializer):
    """

    """
    template_questions = QuestionnaireTemplateQuestionSerializer(many=True)
    parent_order_number = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    order_number = serializers.IntegerField(write_only=True, required=False)
    # this field will contain information that is needed to update a Questionnaire Template
    siblings = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = '__all__'
        extra_kwargs = {'questionnaire_template': {'required': False}}

    def create(self, validated_data):
        if validated_data['questionnaire_template'].is_editable:
            validated_data.pop('children', None)
            template_questions = validated_data.pop('template_questions')

            # Get the block siblings to update
            siblings_to_update = validated_data.pop('siblings', [])
            for sibling in siblings_to_update:
                block_id = sibling.pop('block_id', None)
                # Check if blocks are from the same questionnaire template
                block_to_update = QuestionnaireTemplateBlock.objects.filter(pk=block_id, questionnaire_template=validated_data['questionnaire_template']).first()

                if block_to_update is not None:
                    for attr, value in sibling.get('block_changes', {}).items():
                        setattr(block_to_update, attr, value)
                    block_to_update.save()

            template_block = QuestionnaireTemplateBlock.objects.create(**validated_data)

            for template_block_question in template_questions:
                template_block_question['questionnaire_template'] = template_block.questionnaire_template.id
                template_block_question['template_block'] = template_block.id
                template_block_question_ser = QuestionnaireTemplateQuestionSerializer(data=template_block_question)
                template_block_question_ser.is_valid(raise_exception=True)
                template_block_question_ser.save()

            return template_block
        raise serializers.ValidationError('The Questionnaire Template this Block belongs to is not editable')

    def update(self, instance, validated_data):
        template_questions = validated_data.pop('template_questions', list())
        if instance.questionnaire_template.is_editable:
            # Get the block siblings to update
            siblings = validated_data.pop('siblings', [])
            for sibling in siblings:
                block_id = sibling.pop('block_id')
                # Check if blocks are from the same questionnaire template
                block_to_update = QuestionnaireTemplateBlock.objects.filter(pk=block_id, questionnaire_template=validated_data['questionnaire_template']).first()

                if block_to_update is not None:
                    for attr, value in sibling['block_changes'].items():
                        setattr(block_to_update, attr, value)
                    block_to_update.save()

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class QuestionnaireSerializer(serializers.ModelSerializer):
    """

    """
    blocks = QuestionnaireBlockSerializer(many=True, required=False)

    class Meta:
        model = Questionnaire
        fields = '__all__'  #('title', 'blocks', 'template',)


    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('blocks__questions__question_choices')
        return queryset

    def create(self, validated_data):
        # print(validated_data)
        blocks = validated_data.pop('blocks', None)
        questionnaire = Questionnaire.objects.create(**validated_data)

        parents = {}
        if blocks:
            for block in blocks:
                block['questionnaire'] = questionnaire.id
                if block['parent_order_number'] is None:
                    order_number = block.pop('order_number', None)
                    block.pop('parent_order_number', None)
                    block['parent_block'] = None
                    block_ser = QuestionnaireBlockSerializer(data=block)
                    block_ser.is_valid(raise_exception=True)
                    block_ser.save()
                    parents[order_number] = block_ser.instance.id
                else:
                    block['parent_block'] = parents[block['parent_order_number']]
                    order_number = block.pop('order_number', None)
                    block.pop('parent_order_number', None)
                    block_ser = QuestionnaireBlockSerializer(data=block)
                    block_ser.is_valid(raise_exception=True)
                    block_ser.save()
                    parents[order_number] = block_ser.instance.id
        return questionnaire


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """

    """
    template_blocks = QuestionnaireTemplateBlockSerializer(many=True, required=False)

    class Meta:
        model = QuestionnaireTemplate
        fields = '__all__'
        extra_kwargs = {'is_editable': {'read_only': True}}

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('template_blocks__template_questions__template_question_choices')
        return queryset

    def create(self, validated_data):
        template_blocks = validated_data.pop('template_blocks', None)
        questionnaire_template = QuestionnaireTemplate.objects.create(**validated_data)

        parents = {}
        if template_blocks:
            for template_block in template_blocks:
                template_block['questionnaire_template'] = questionnaire_template.id
                if template_block['parent_order_number'] is None:
                    order_number = template_block.pop('order_number', None)
                    template_block.pop('parent_order_number', None)
                    template_block['parent_block'] = None
                    template_block_ser = QuestionnaireTemplateBlockSerializer(data=template_block)
                    template_block_ser.is_valid(raise_exception=True)
                    template_block_ser.save()
                    parents[order_number] = template_block_ser.instance.id
                else:
                    template_block['parent_block'] = parents[template_block['parent_order_number']]
                    order_number = template_block.pop('order_number', None)
                    template_block.pop('parent_order_number', None)
                    template_block_ser = QuestionnaireTemplateBlockSerializer(data=template_block)
                    template_block_ser.is_valid(raise_exception=True)
                    template_block_ser.save()
                    parents[order_number] = template_block_ser.instance.id

        return questionnaire_template

    def update(self, instance, validated_data):
        # If template blocks is a list of ordered dicts, pop it from validated_data
        # so that it won't throw an error on update.
        template_blocks = validated_data.get('template_blocks', [])
        pop_blocks = len(template_blocks) > 0 and isinstance(template_blocks[0], OrderedDict)
        if pop_blocks:
            validated_data.pop('template_blocks')
        if self.instance.is_editable:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class CrossIndexTemplateSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CrossIndexTemplate
        fields = '__all__'

    def validate(self, attrs):
        questionnaire_template = attrs.get('questionnaire_template', None)
        question_templates = attrs.get('question_templates', [])

        for template_question in question_templates:
            if template_question.questionnaire_template.id != questionnaire_template.id:
                raise serializers.ValidationError({'question_templates': 'Template Questions don\'t correspond to the Questionnaire Template'})
        return attrs


class CrossIndexSerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = CrossIndex
        fields = '__all__'

    def validate(self, attrs):
        questionnaire = attrs.get('questionnaire', None)
        question = attrs.get('questions', [])

        for question in question:
            if question.questionnaire.id != questionnaire.id:
                raise serializers.ValidationError({'question': 'Questions don\'t correspond to the Questionnaire'})
        return attrs

