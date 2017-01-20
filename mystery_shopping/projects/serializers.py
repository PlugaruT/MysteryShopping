from collections import namedtuple

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment

from mystery_shopping.companies.serializers import CompanyElementSerializer
from mystery_shopping.cxi.serializers import WhyCauseSerializer
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.questionnaires.serializers import QuestionnaireScriptSerializer, \
    DetractorRespondentForTenantSerializer, QuestionnaireTemplateSerializerGET
from mystery_shopping.questionnaires.serializers import QuestionnaireSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.questionnaires.models import QuestionnaireQuestion
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.utils import update_attributes
from mystery_shopping.users.serializers import UserSerializer, UserSerializerGET, ShopperSerializer


class EvaluationAssessmentCommentSerializer(serializers.ModelSerializer):
    """
    Default Evaluation Assessment Comment serializer.
    """
    class Meta:
        model = EvaluationAssessmentComment
        fields = '__all__'


class EvaluationAssessmentCommentSerializerGET(EvaluationAssessmentCommentSerializer):
    """
    Nested Evaluation Assessment Comment serializer, with .

    """
    commenter = UserSerializer(read_only=True)

    class Meta:
        model = EvaluationAssessmentComment
        fields = '__all__'


class EvaluationAssessmentLevelSerializer(serializers.ModelSerializer):
    """
    Default Evaluation Assessment Level serializer.
    """

    class Meta:
        model = EvaluationAssessmentLevel
        fields = '__all__'
        extra_kwargs = {
            'consultants': {
                'allow_empty': True,
                'many': True
            }
        }


class EvaluationAssessmentLevelSerializerGET(EvaluationAssessmentLevelSerializer):
    """
    Nested Evaluation Assessment Level serializer.
    """
    project_manager = UserSerializer(read_only=True)
    consultants = UserSerializer(read_only=True, many=True)
    comments = EvaluationAssessmentCommentSerializer(source='evaluation_assessment_comments', read_only=True, many=True)

    class Meta:
        model = EvaluationAssessmentLevel
        fields = '__all__'
        extra_kwargs = {
            'next_level': {
                'read_only': True
            }
        }


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """
    Default serializer for Research Methodology
    """
    project_id = serializers.IntegerField(required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'
        extra_kwargs = {
            'scripts': {
                'allow_empty': True,
                'required': False
            },
            'tenant': {
                'required': False
            }
        }

    def _extract_attributes(self, data):
        Fields = namedtuple('Fields', ['project_id', 'scripts', 'questionnaires', 'company_elements'])
        fields = Fields(project_id=data.pop('project_id', None),
                        scripts=data.pop('scripts', []),
                        questionnaires=data.pop('questionnaires', []),
                        company_elements=data.pop('company_elements', []))
        return fields

    def _set_many_to_many(self, instance, fields):
        instance.scripts.set(fields.scripts)
        instance.questionnaires.set(fields.questionnaires)
        instance.company_elements.set(fields.company_elements)


    def create(self, validated_data):
        popped_fields = self._extract_attributes(validated_data)

        research_methodology = ResearchMethodology.objects.create(**validated_data)

        self._set_many_to_many(research_methodology, popped_fields)
        self.link_research_methodology_to_project(popped_fields.project_id, research_methodology)

        return research_methodology

    def update(self, instance, validated_data):
        popped_fields = self._extract_attributes(validated_data)

        self._set_many_to_many(instance, popped_fields)
        self.link_research_methodology_to_project(popped_fields.project_id, instance)

        update_attributes(validated_data, instance)
        instance.save()

        return instance

    @staticmethod
    def link_research_methodology_to_project(project_id, research_methodology):
        if project_id:
            project_to_set = get_object_or_404(Project, pk=project_id)
            if project_to_set:
                project_to_set.research_methodology = research_methodology
                project_to_set.save()


class ResearchMethodologySerializerGET(ResearchMethodologySerializer):
    """
    GET Research Methodology serializer that uses nested serializers.
    """
    scripts = QuestionnaireScriptSerializer(many=True, read_only=True)
    questionnaires = QuestionnaireTemplateSerializerGET(many=True, read_only=True)
    company_elements = CompanyElementSerializer(many=True, required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    """
    Default serializer for project
    """
    research_methodology = ResearchMethodologySerializer(required=False)

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'shoppers': {
                'allow_empty': True,
                'required': False
            }
        }

    def validate(self, attrs):
        for value, key in attrs.items():
            print(value, key)
        return attrs

    def _set_research_methodology(self, project, research_methodology_instance, data):
        data['project_id'] = project.id
        data['scripts'] = list(map(lambda x: x.id, data.get('scripts', [])))
        data['company_elements'] = list(map(lambda x: x.id, data.get('company_elements', [])))
        data['questionnaires'] = list(
            map(lambda x: x.id, data.get('questionnaires', [])))
        data['tenant'] = data['tenant'].id
        research_methodology_ser = ResearchMethodologySerializer(instance=research_methodology_instance,
                                                                 data=data)
        research_methodology_ser.is_valid(raise_exception=True)
        research_methodology_ser.save()
        return research_methodology_ser.instance

    def create(self, validated_data):
        research_methodology = validated_data.pop('research_methodology', None)
        research_methodology['tenant'] = validated_data['tenant']
        consultants = validated_data.pop('consultants', [])
        shoppers = validated_data.pop('shoppers', [])

        # user.set_perm(); from django. blablabla

        project = Project.objects.create(**validated_data)

        project.consultants.set(consultants)
        project.shoppers.set(shoppers)

        if research_methodology is not None:
            project.research_methodology = self._set_research_methodology(project=project,
                                                                          research_methodology_instance=None,
                                                                          data=research_methodology)

        return project

    def update(self, instance, validated_data):
        consultants = validated_data.pop('consultants', [])
        shoppers = validated_data.pop('shoppers', [])
        research_methodology = validated_data.pop('research_methodology', None)

        instance.consultants.set(consultants)
        instance.shoppers.set(shoppers)

        if research_methodology is not None:
            research_methodology_instance = instance.research_methodology
            instance.research_methodology = self._set_research_methodology(project=instance,
                                                                           research_methodology_instance=research_methodology_instance,
                                                                           data=research_methodology)

        update_attributes(validated_data, instance)
        instance.save()

        return instance


class ProjectSerializerGET(ProjectSerializer):
    """
    Get serializer for Project
    """
    research_methodology = ResearchMethodologySerializerGET(required=False)
    company = CompanyElementSerializer(read_only=True)
    shoppers = UserSerializerGET(many=True, read_only=True)
    project_manager = UserSerializerGET(read_only=True)
    consultants = UserSerializerGET(read_only=True, many=True)
    evaluation_assessment_levels = EvaluationAssessmentLevelSerializer(read_only=True, many=True)
    cxi_indicators = serializers.DictField(source='get_indicators_list', read_only=True)
    disabled_elements = serializers.ListField(source='get_company_elements_with_evaluations', read_only=True)
    is_questionnaire_editable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectShortSerializer(serializers.ModelSerializer):
    """
    Project serializer that includes only the date fields for evaluation's representation of a project.
    """

    class Meta:
        model = Project
        fields = ('period_start', 'period_end')


class EvaluationSerializer(serializers.ModelSerializer):
    """
    Default Evaluation serializer that can update questionnaire answers and such.
    """
    detractor_info = DetractorRespondentForTenantSerializer(write_only=True, required=False)

    class Meta:
        model = Evaluation
        fields = '__all__'
        extra_kwargs = {
            'saved_by_user': {
                'required': False
            }
        }

    @staticmethod
    def setup_eager_loading(queryset):
        # queryset = queryset.select_related('shopper__user', 'entity__city', 'questionnaire',
        #                                    'questionnaire_template', 'section')
        # queryset = queryset.prefetch_related('questionnaire__blocks__questions__question_choices',
        #                                      'entity__employees__company',
        #                                      'entity__managers__user',
        #                                      'entity__sections__managers',
        #                                      'entity__sections__employees',
        #                                      'section__managers',
        #                                      'section__employees__company')
        return queryset

    def create(self, validated_data):
        questionnaire_template = validated_data.get('questionnaire_template', None)

        questionnaire_to_create = self._clone_questionnaire(questionnaire_template)
        questionnaire_to_create_ser = QuestionnaireSerializer(data=questionnaire_to_create)
        questionnaire_to_create_ser.is_valid(raise_exception=True)
        questionnaire_to_create_ser.save()

        cross_indexes = questionnaire_to_create.get('template_cross_indexes', [])
        if cross_indexes is not []:
            questionnaire_to_create_ser.instance.create_cross_indexes(cross_indexes)

        validated_data['questionnaire'] = questionnaire_to_create_ser.instance

        evaluation = Evaluation.objects.create(**validated_data)
        return evaluation

    def update(self, instance, validated_data):
        current_status = instance.status
        questionnaire = validated_data.pop('questionnaire', None)

        detractor_info = validated_data.pop('detractor_info', None)
        detractor_instance = None
        if detractor_info:
            detractor_instance = self._create_detractor(detractor_info)
        self.set_evaluation_to_detractor(detractor_instance, instance)

        if questionnaire and current_status in EvaluationStatus.EDITABLE_STATUSES:
            self._update_questionnaire_answers(questionnaire)

            if validated_data.get('status', EvaluationStatus.PLANNED) == EvaluationStatus.PLANNED:
                instance.status = EvaluationStatus.DRAFT
            else:
                instance.status = validated_data.get('status')

            if validated_data.get('status') == EvaluationStatus.SUBMITTED and validated_data.get('type') == 'm':
                instance.questionnaire.calculate_score()

        instance.questionnaire = Questionnaire.objects.get(pk=instance.questionnaire.pk)
        instance.questionnaire.save()

        update_attributes(validated_data, instance)
        instance.save()
        return instance

    def _update_questionnaire_answers(self, questionnaire):
        for block in questionnaire.get('blocks', []):
            for question in block.get('questions', []):
                self._update_question_answer(question)

    @staticmethod
    def _update_question_answer(question):
        question_instance = QuestionnaireQuestion.objects.get(questionnaire=question.get('questionnaire'),
                                                              pk=question.get('question_id'))
        question_instance.answer = question.get('answer')
        question_instance.score = question.get('score')
        question_instance.answer_choices = question.get('answer_choices', [])
        question_instance.comment = question.get('comment')
        why_causes = question.pop('why_causes', [])
        for why_cause in why_causes:
            why_cause['question'] = question_instance.id
            why_cause_ser = WhyCauseSerializer(data=why_cause)
            why_cause_ser.is_valid(raise_exception=True)
            why_cause_ser.save()
        question_instance.save()

    @staticmethod
    def set_evaluation_to_detractor(detractor_instance, evaluation):
        if detractor_instance:
            detractor_instance.evaluation = evaluation
            detractor_instance.number_of_questions = evaluation.get_indicator_questions().filter(score__lte=6).count()
            detractor_instance.save()

    @staticmethod
    def _create_detractor(detractor_info, evaluation_id=None):
        detractor_info['evaluation'] = evaluation_id
        detractor_to_create = DetractorRespondentForTenantSerializer(data=detractor_info)
        detractor_to_create.is_valid(raise_exception=True)
        detractor_to_create.save()
        return detractor_to_create.instance

    def _clone_questionnaire(self, questionnaire_template):
        questionnaire_template_serialized = QuestionnaireTemplateSerializer(questionnaire_template)
        questionnaire_to_create = dict(questionnaire_template_serialized.data)
        questionnaire_to_create['template'] = questionnaire_template.id
        questionnaire_to_create['blocks'] = self.build_blocks(questionnaire_to_create.pop('template_blocks'))
        return questionnaire_to_create

    def build_blocks(self, blocks):
        for block in blocks:
            block['template_block'] = block.get('id')
            block['order_number'] = block.pop('id')
            block['parent_order_number'] = block.pop('parent_block')
            block['questions'] = self.build_questions(block.pop('template_questions'))
        return blocks

    @staticmethod
    def build_questions(questions):
        for question in questions:
            question['template_question'] = question.pop('id')
            question['question_choices'] = question.pop('template_question_choices')
        return questions

    @staticmethod
    def _check_if_indicator_question_has_null_score(question):
        if question['type'] == QuestionType.INDICATOR_QUESTION:
            if question['score'] is None:
                raise serializers.ValidationError('Indicator Question isn\'t allowed to have null score')



class EvaluationSerializerGET(EvaluationSerializer):
    """
    GET Evaluation serializer that uses nested serializers.
    """
    shopper = UserSerializerGET(read_only=True)
    questionnaire_script = QuestionnaireScriptSerializer(read_only=True)
    questionnaire = QuestionnaireSerializer(read_only=True)
    company_element = CompanyElementSerializer(read_only=True)
    project = ProjectShortSerializer(read_only=True)

    class Meta:
        model = Evaluation
        fields = '__all__'


class ProjectStatisticsForCompanySerializer(serializers.ModelSerializer):
    """
        Serializer for company view that will contain only time,
        date and places/people to asses
    """

    class Meta:
        model = Evaluation
        fields = ('id', 'time_accomplished', 'company_element')

class ProjectStatisticsForCompanySerializerGET(ProjectStatisticsForCompanySerializer):
    """
        Serializer class for client view for GET requests
    """
    company_element = CompanyElementSerializer(read_only=True)


class ProjectStatisticsForTenantSerializer(serializers.ModelSerializer):
    """
        Serializer for tenant view that will contain only time,
        date and places/people to asses and collector information
    """

    class Meta:
        model = Evaluation
        fields = ('id', 'time_accomplished', 'company_element', 'shopper')

class ProjectStatisticsForTenantSerializerGET(ProjectStatisticsForTenantSerializer):
    """
        Serializer class for tenant view for GET requests
    """
    company_element = CompanyElementSerializer(read_only=True)
    shopper = UserSerializerGET(read_only=True)
