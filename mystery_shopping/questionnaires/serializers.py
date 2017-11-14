from django.shortcuts import get_object_or_404
from rest_framework import serializers

from mystery_shopping.cxi.serializers import WhyCauseSerializer
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import CrossIndexQuestion, QuestionnaireTemplateStatus, CustomWeight
from mystery_shopping.respondents.models import Respondent
from mystery_shopping.users.serializers import UserSerializerGET
from .models import CrossIndex
from .models import CrossIndexQuestionTemplate
from .models import CrossIndexTemplate
from .models import Questionnaire
from .models import QuestionnaireBlock
from .models import QuestionnaireQuestion
from .models import QuestionnaireQuestionChoice
from .models import QuestionnaireScript
from .models import QuestionnaireTemplate
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireTemplateQuestionChoice
from .utils import update_attributes


class QuestionnaireTemplateQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = QuestionnaireTemplateQuestionChoice
        fields = '__all__'
        extra_kwargs = {
            'template_question': {
                'required': False
            }
        }

    def update(self, instance, validated_data):
        if not instance.template_question.questionnaire_template.is_editable:
            raise serializers.ValidationError('You are not allowed to do this action')
        update_attributes(instance, validated_data)
        instance.save()
        return instance


class QuestionnaireQuestionChoiceSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = QuestionnaireQuestionChoice
        fields = '__all__'
        extra_kwargs = {
            'question': {
                'required': False
            }
        }


class QuestionnaireScriptSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = QuestionnaireScript
        fields = ('id', 'title', 'description',)


class CustomWeightSerializer(serializers.ModelSerializer):
    """
    serializer for custom weight model
    """

    class Meta:
        model = CustomWeight
        fields = '__all__'


class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    """

    """
    question_choices = QuestionnaireQuestionChoiceSerializer(many=True, required=False)
    why_causes = WhyCauseSerializer(many=True, required=False)
    question_id = serializers.IntegerField(write_only=True, required=False)
    allow_why_causes = serializers.BooleanField(source='template_question.allow_why_causes', read_only=True)
    has_other_choice = serializers.BooleanField(source='template_question.has_other_choice', read_only=True)

    class Meta:
        model = QuestionnaireQuestion
        fields = '__all__'
        extra_kwargs = {
            'block': {
                'required': False
            },
            'questionnaire': {
                'required': False
            },
            'answer_choices': {
                'required': False,
                'allow_empty': True
            }
        }

    def create(self, validated_data):
        question_choices = validated_data.pop('question_choices', [])
        why_causes = validated_data.pop('why_causes', [])
        question = QuestionnaireQuestion.objects.create(**validated_data)
        self._create_question_choices(question_choices, question.id)
        self._create_why_causes(why_causes, question.id)
        return question

    def update(self, instance, validated_data):
        validated_data.pop('question_choices', [])
        update_attributes(instance, validated_data)
        instance.save()
        return instance

    @staticmethod
    def _create_question_choices(question_choices, question_id):
        for question_choice in question_choices:
            question_choice['question'] = question_id
            question_choice_ser = QuestionnaireQuestionChoiceSerializer(data=question_choice)
            question_choice_ser.is_valid(raise_exception=True)
            question_choice_ser.save()

    @staticmethod
    def _create_why_causes(why_causes, question_id):
        for why_cause in why_causes:
            why_cause['question'] = question_id
            why_cause_ser = WhyCauseSerializer(data=why_cause)
            why_cause_ser.is_valid(raise_exception=True)
            why_cause_ser.save()


class QuestionnaireTemplateQuestionSerializer(serializers.ModelSerializer):
    """

    """
    custom_weights = CustomWeightSerializer(many=True, read_only=True)
    template_question_choices = QuestionnaireTemplateQuestionChoiceSerializer(many=True, required=False)
    siblings = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireTemplateQuestion
        fields = '__all__'
        extra_kwargs = {
            'questionnaire_template': {
                'required': False
            },
            'template_block': {
                'required': False
            }
        }

    def pop_special_flags(self, data):
        data.pop('allow_why_causes', None)
        data.pop('has_other_choice', None)
        data.pop('new_algorithm', None)

    def create(self, validated_data):
        if not validated_data['questionnaire_template'].is_editable:
            raise serializers.ValidationError('The Questionnaire Template this Question belongs to is not editable')

        self.pop_special_flags(validated_data)
        template_question_choices = validated_data.pop('template_question_choices', [])
        siblings_to_update = validated_data.pop('siblings', [])

        template_question = QuestionnaireTemplateQuestion.objects.create(**validated_data)
        self._create_custom_weights(template_question)
        self._create_template_question_choices(template_question_choices, template_question.id)
        template_question.update_siblings(siblings_to_update, template_question.template_block)
        return template_question

    def update(self, instance, validated_data):
        if not instance.questionnaire_template.is_editable:
            raise serializers.ValidationError('You are not allowed to do this action')

        instance.prepare_to_update()
        self.pop_special_flags(validated_data)
        template_question_choices = validated_data.pop('template_question_choices', [])
        siblings_to_update = validated_data.pop('siblings', [])

        self._create_template_question_choices(template_question_choices, instance.id)
        update_attributes(instance, validated_data)

        instance.update_siblings(siblings_to_update, validated_data.get('template_block'))

        instance.save()
        return instance

    @staticmethod
    def _create_template_question_choices(template_question_choices, template_question_id):
        for template_question_choice in template_question_choices:
            template_question_choice['template_question'] = template_question_id
            template_question_choice_ser = QuestionnaireTemplateQuestionChoiceSerializer(
                data=template_question_choice)
            template_question_choice_ser.is_valid(raise_exception=True)
            template_question_choice_ser.save()

    @staticmethod
    def _create_custom_weights(template_question):
        if template_question.type == QuestionType.INDICATOR_QUESTION:
            custom_weights_name = CustomWeight.objects.get_weights_names_for_questionnaire(
                template_question.questionnaire_template.pk)
            template_question.create_custom_weights(custom_weights_name)


class QuestionnaireBlockSerializer(serializers.ModelSerializer):
    """

    """
    questions = QuestionnaireQuestionSerializer(many=True)
    parent_order_number = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    order_number = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireBlock
        fields = '__all__'
        extra_kwargs = {
            'questionnaire': {
                'required': False
            },
            'score': {
                'required': False
            }
        }

    def create(self, validated_data):
        validated_data.pop('children', None)
        questions = validated_data.pop('questions')

        block = QuestionnaireBlock.objects.create(**validated_data)

        for question in questions:
            question['template_question'] = question['template_question'].id
            question['questionnaire'] = block.questionnaire.id
            question['block'] = block.id
            block_question_ser = QuestionnaireQuestionSerializer(data=question)
            block_question_ser.is_valid(raise_exception=True)
            block_question_ser.save()
        return block

    def update(self, instance, validated_data):
        update_attributes(instance, validated_data)
        return instance


class QuestionnaireTemplateBlockSerializer(serializers.ModelSerializer):
    """

    """
    template_questions = QuestionnaireTemplateQuestionSerializer(many=True)
    parent_order_number = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    order_number = serializers.IntegerField(write_only=True, required=False)
    siblings = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = QuestionnaireTemplateBlock
        fields = '__all__'
        extra_kwargs = {
            'questionnaire_template': {
                'required': False
            }
        }

    def create(self, validated_data):
        if not validated_data['questionnaire_template'].is_editable:
            raise serializers.ValidationError('The Questionnaire Template this Block belongs to is not editable')
        validated_data.pop('children', None)
        template_questions = validated_data.pop('template_questions')
        siblings_to_update = validated_data.pop('siblings', [])
        self.update_block_siblings(siblings_to_update, validated_data)
        template_block = QuestionnaireTemplateBlock.objects.create(**validated_data)
        self.create_template_block_questions(template_questions, template_block)
        return template_block

    def update(self, instance, validated_data):
        validated_data.pop('template_questions', list())
        if not instance.questionnaire_template.is_editable:
            raise serializers.ValidationError('You are not allowed to do this action')
        siblings = validated_data.pop('siblings', [])
        self.update_block_siblings(siblings, validated_data)
        update_attributes(instance, validated_data)
        instance.save()
        return instance

    @staticmethod
    def create_template_block_questions(template_questions, template_block):
        for template_block_question in template_questions:
            template_block_question['questionnaire_template'] = template_block.questionnaire_template.id
            template_block_question['template_block'] = template_block.id
            template_block_question_ser = QuestionnaireTemplateQuestionSerializer(data=template_block_question)
            template_block_question_ser.is_valid(raise_exception=True)
            template_block_question_ser.save()

    @staticmethod
    def update_block_siblings(siblings_to_update, validated_data):
        for sibling in siblings_to_update:
            block_id = sibling.pop('block_id')
            block_to_update = get_object_or_404(QuestionnaireTemplateBlock,
                                                pk=block_id,
                                                questionnaire_template=validated_data['questionnaire_template'])
            if block_to_update is not None:
                update_attributes(block_to_update, sibling['block_changes'])
                block_to_update.save()


class CrossIndexQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrossIndexQuestion
        fields = '__all__'


class CrossIndexSerializer(serializers.ModelSerializer):
    """

    """
    questions = CrossIndexQuestionSerializer(source='cross_index_questions', many=True)

    class Meta:
        model = CrossIndex
        fields = '__all__'


class QuestionnaireSerializer(serializers.ModelSerializer):
    """

    """
    blocks = QuestionnaireBlockSerializer(many=True, required=False)
    cross_indexes = CrossIndexSerializer(many=True, required=False, read_only=True)
    description = serializers.CharField(source='template.description', read_only=True)

    class Meta:
        model = Questionnaire
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('blocks__questions__question_choices')
        return queryset

    def create(self, validated_data):
        blocks = validated_data.pop('blocks', [])
        questionnaire = Questionnaire.objects.create(**validated_data)

        parents = {}

        for block in blocks:
            block['questionnaire'] = questionnaire.id
            if block['parent_order_number'] is None:
                block.pop('parent_order_number')
                block['parent_block'] = None
                # When sending id it get's the object, but this throws an error
                # so I'm "reverting" the process
                self.create_block(block, parents)
            else:
                block['parent_block'] = parents[block.pop('parent_order_number')]
                # When sending id it gets the object, but this throws an error
                # so I'm "reverting" the process
                self.create_block(block, parents)
        return questionnaire

    @staticmethod
    def create_block(block, parents):
        order_number = block.pop('order_number')
        block['template_block'] = block['template_block'].id
        for question in block['questions']:
            question['template_question'] = question['template_question'].id
        block_ser = QuestionnaireBlockSerializer(data=block)
        block_ser.is_valid(raise_exception=True)
        block_ser.save()
        parents[order_number] = block_ser.instance.id


class CrossIndexQuestionTemplateSerializer(serializers.ModelSerializer):
    """

    """

    class Meta:
        model = CrossIndexQuestionTemplate
        fields = ('template_question', 'weight')
        extra_kwargs = {
            'template_cross_index': {
                'required': False
            }
        }


class CrossIndexTemplateSerializer(serializers.ModelSerializer):
    """

    """
    template_questions = CrossIndexQuestionTemplateSerializer(source='cross_index_template_questions',
                                                              many=True,
                                                              required=False)

    class Meta:
        model = CrossIndexTemplate
        fields = '__all__'

    def validate(self, attrs):
        questionnaire_template = attrs.get('questionnaire_template', None)
        template_questions = attrs.get('cross_index_template_questions', [])
        template_question_ids = [template_question['template_question'].id for template_question in template_questions]

        if not self.all_unique(template_question_ids):
            raise serializers.ValidationError({
                'question_templates': 'Template Questions already in Cross Index Template list'
            })

        for template_question in template_questions:
            if template_question.questionnaire_template.id != questionnaire_template.id:
                raise serializers.ValidationError({
                    'question_templates': 'Template Questions don\'t correspond to the Questionnaire Template'
                })
        return attrs

    def create(self, validated_data):
        template_questions = validated_data.pop('cross_index_template_questions', [])
        cross_template = CrossIndexTemplate.objects.create(**validated_data)
        self.create_template_question(template_questions, cross_template)
        return cross_template

    def update(self, instance, validated_data):
        template_questions = validated_data.pop('cross_index_template_questions', [])
        instance.template_questions.clear()
        self.create_template_question(template_questions, instance)
        update_attributes(instance, validated_data)
        instance.save()
        return instance

    @staticmethod
    def all_unique(arr):
        """
        Function for verifying if all elements of a list are unique
        :param arr: the list to check
        :return: boolean value, True if all elements are unique, False otherwise
        """
        return len(arr) == len(set(arr))

    @staticmethod
    def create_template_question(template_questions, template_cross_indexes):
        for template_question in template_questions:
            CrossIndexQuestionTemplate.objects.create(template_cross_indexes=template_cross_indexes,
                                                      template_question=template_question['template_question'],
                                                      weight=template_question['weight'])


class QuestionnaireTemplateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireTemplateStatus
        fields = '__all__'


class QuestionnaireTemplateSerializer(serializers.ModelSerializer):
    """
    Default Questionnaire Template serializer.
    """
    template_blocks = QuestionnaireTemplateBlockSerializer(many=True, required=False)
    template_cross_indexes = CrossIndexTemplateSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = QuestionnaireTemplate
        fields = '__all__'
        extra_kwargs = {
            'is_editable': {
                'read_only': True
            },
            'status': {
                'required': False
            }
        }

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('template_blocks__template_questions__template_question_choices')
        return queryset

    def create(self, validated_data):
        template_blocks = validated_data.pop('template_blocks', [])
        questionnaire_template = QuestionnaireTemplate.objects.create(**validated_data)

        parents = {}
        for template_block in template_blocks:
            template_block['questionnaire_template'] = questionnaire_template.id
            parent_order_number = template_block.pop('parent_order_number', None)
            if parent_order_number is None:
                template_block['parent_block'] = None
                self.create_template_block(template_block, parents)
            else:
                template_block['parent_block'] = parents[parent_order_number]
                self.create_template_block(template_block, parents)

        return questionnaire_template

    def update(self, instance, validated_data):
        if not instance.is_editable:
            raise serializers.ValidationError('You are not allowed to do this action')

        validated_data.pop('template_blocks', [])
        update_attributes(instance, validated_data)
        instance.save()
        return instance

    def create_template_block(self, template_block, parents):
        order_number = template_block.pop('order_number', None)
        self.remove_ids(template_block)
        template_block_ser = QuestionnaireTemplateBlockSerializer(data=template_block)
        template_block_ser.is_valid(raise_exception=True)
        template_block_ser.save()
        parents[order_number] = template_block_ser.instance.id

    @staticmethod
    def remove_ids(template_block):
        for template_question in template_block['template_questions']:
            template_question.pop('questionnaire_template', None)
            template_question.pop('template_block', None)
            for template_question_choice in template_question['template_question_choices']:
                template_question_choice.pop('template_question', None)


class QuestionnaireTemplateSerializerGET(QuestionnaireTemplateSerializer):
    """
    Nested Questionnaire Template serializer.
    """
    status = QuestionnaireTemplateStatusSerializer(read_only=True)
    created_by = UserSerializerGET(read_only=True)

    class Meta:
        model = QuestionnaireTemplate
        fields = '__all__'


class QuestionSimpleSerializer(serializers.ModelSerializer):
    """
        Serializes questions simpler including needed fields
    """

    class Meta:
        model = QuestionnaireQuestion
        fields = ('id', 'question_body', 'score')


class BlockSimpleSerializer(serializers.ModelSerializer):
    """
        Serializes blocks simpler including needed fields
    """
    questions = QuestionSimpleSerializer(many=True)

    class Meta:
        model = QuestionnaireBlock
        fields = ('id', 'title', 'score', 'questions')


class QuestionnaireSimpleSerializer(serializers.ModelSerializer):
    """
        Serializes questionnaires simpler including needed fields
    """
    blocks = BlockSimpleSerializer(many=True)

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'score', 'blocks')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('blocks__questions')
        return queryset
