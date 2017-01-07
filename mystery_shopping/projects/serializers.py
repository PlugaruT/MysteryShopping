from django.shortcuts import get_object_or_404
from rest_framework import serializers

from mystery_shopping.cxi.serializers import WhyCauseSerializer
from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment

from mystery_shopping.companies.serializers import CompanyElementSerializer

from mystery_shopping.companies.serializers import CompanySerializer

from mystery_shopping.questionnaires.serializers import QuestionnaireScriptSerializer, \
    DetractorRespondentForTenantSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.questionnaires.models import QuestionnaireQuestion, QuestionnaireScript
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.utils import update_attributes
from mystery_shopping.users.serializers import ShopperSerializer
from mystery_shopping.users.serializers import TenantProjectManagerSerializer
from mystery_shopping.users.serializers import TenantConsultantSerializer
from mystery_shopping.users.serializer_fields import TenantUserRelatedField
from mystery_shopping.projects.constants import EvaluationStatus

from mystery_shopping.users.models import Shopper


class EvaluationAssessmentCommentSerializer(serializers.ModelSerializer):
    """

    """
    commenter_repr = TenantUserRelatedField(source='commenter', read_only=True)

    class Meta:
        model = EvaluationAssessmentComment
        fields = '__all__'


class EvaluationAssessmentLevelSerializer(serializers.ModelSerializer):
    """

    """
    next_level = serializers.PrimaryKeyRelatedField(read_only=True)
    project_manager_repr = TenantProjectManagerSerializer(source='project_manager', read_only=True)
    consultants_repr = TenantConsultantSerializer(source='consultants', read_only=True, many=True)
    comments = EvaluationAssessmentCommentSerializer(source='evaluation_assessment_comments', read_only=True, many=True)

    class Meta:
        model = EvaluationAssessmentLevel
        fields = '__all__'
        extra_kwargs = {
            'consultants': {
                'allow_empty': True,
                'many': True
            }
        }


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """

    """
    scripts = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireScript.objects.all(), required=False, many=True)
    scripts_repr = QuestionnaireScriptSerializer(source='scripts', many=True, read_only=True)
    questionnaires_repr = QuestionnaireTemplateSerializer(source='questionnaires', many=True, read_only=True)
    # TODO: handle this new naw on frontend
    company_elements_repr = CompanyElementSerializer(source='company_elements', many=True, required=False)
    project_id = serializers.IntegerField(required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'

    def create(self, validated_data):
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts', [])
        questionnaires = validated_data.pop('questionnaires', [])

        research_methodology = ResearchMethodology.objects.create(**validated_data)

        research_methodology.scripts.set(scripts)
        research_methodology.questionnaires.set(questionnaires)

        self.link_research_methodology_to_project(project_id, research_methodology)

        return research_methodology

    def update(self, instance, validated_data):
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts', [])
        questionnaires = validated_data.pop('questionnaires', [])

        instance.prepare_for_update()

        instance.scripts.set(scripts)
        instance.questionnaires.set(questionnaires)

        self.link_research_methodology_to_project(project_id, instance)

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

    @staticmethod
    def _set_places_to_asses(research_methodology, places_to_assess):
        # places_to_set = list()
        # for place_to_assess in places_to_assess:
        #     place_to_assess['research_methodology'] = research_methodology
        #     places_to_set.append(PlaceToAssess.objects.create(**place_to_assess))
        # research_methodology.places_to_assess.set(places_to_set)
        pass

class ProjectSerializer(serializers.ModelSerializer):
    """

    """
    company_repr = CompanySerializer(source='company', read_only=True)
    shoppers_repr = ShopperSerializer(source='shoppers', many=True, read_only=True)
    project_manager_repr = TenantProjectManagerSerializer(source='project_manager', read_only=True)
    research_methodology = ResearchMethodologySerializer(required=False)
    shoppers = serializers.PrimaryKeyRelatedField(queryset=Shopper.objects.all(), many=True, allow_null=True,
                                                  required=False)
    consultants_repr = TenantConsultantSerializer(source='consultants', read_only=True, many=True)
    evaluation_assessment_levels_repr = EvaluationAssessmentLevelSerializer(source='evaluation_assessment_levels',
                                                                            read_only=True, many=True)
    cxi_indicators = serializers.DictField(source='get_indicators_list', read_only=True)
    # TODO: change this for the new structure
    editable_places = serializers.ListField(source='get_editable_places', read_only=True)
    is_questionnaire_editable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'graph_config': {
                'required': False
            }
        }

    def create(self, validated_data):
        research_methodology = validated_data.pop('research_methodology', None)
        consultants = validated_data.pop('consultants', [])
        validated_data.pop('shoppers', None)

        # user.set_perm(); from django. blablabla

        project = Project.objects.create(**validated_data)

        project.consultants.set(consultants)

        if research_methodology is not None:
            research_methodology['project_id'] = project.id
            research_methodology['scripts'] = list(map(lambda x: x.id, research_methodology.get('scripts', [])))
            research_methodology['questionnaires'] = list(
                map(lambda x: x.id, research_methodology.get('questionnaires', [])))
            research_methodology['tenant'] = research_methodology['tenant'].id
            research_methodology_ser = ResearchMethodologySerializer(data=research_methodology)
            research_methodology_ser.is_valid(raise_exception=True)
            research_methodology_ser.save()

        return project

    def update(self, instance, validated_data):
        consultants = validated_data.pop('consultants', [])
        research_methodology = validated_data.pop('research_methodology', None)

        instance.consultants.set(consultants)

        if research_methodology is not None:
            research_methodology_instance = instance.research_methodology
            research_methodology['project_id'] = instance.id
            research_methodology['tenant'] = research_methodology['tenant'].id

            # Map list of instances to list of instance id's, so that when calling serializer.is_valid method, it won't
            # throw the "expected id, got instance" error.
            research_methodology['scripts'] = list(map(lambda x: x.id, research_methodology.get('scripts', [])))
            research_methodology['questionnaires'] = list(
                map(lambda x: x.id, research_methodology.get('questionnaires', [])))

            # Append '_repr' suffix to places_to_assess and people_to_assess fields such that when calling
            # ResearchMethodologySerializer's validation, it won't set these values to empty lists, because of not
            # finding 'places_to_assess_repr' values in data dict
            research_methodology['places_to_assess_repr'] = research_methodology['places_to_assess']
            for place in research_methodology['places_to_assess_repr']:
                place['place_type'] = place.get('place_type').id
                try:
                    del place['research_methodology']
                except KeyError:
                    pass

            research_methodology['people_to_assess_repr'] = research_methodology['people_to_assess']
            for person in research_methodology['people_to_assess_repr']:
                person['person_type'] = person.get('person_type').id
                try:
                    del person['research_methodology']
                except KeyError:
                    pass

            if research_methodology_instance is not None:
                research_methodology_ser = ResearchMethodologySerializer(research_methodology_instance,
                                                                         data=research_methodology)
            else:
                research_methodology_ser = ResearchMethodologySerializer(data=research_methodology)
            research_methodology_ser.is_valid(raise_exception=True)
            research_methodology_ser.save()
            instance.research_methodology = research_methodology_ser.instance

        update_attributes(validated_data, instance)
        instance.save()

        return instance


class ProjectShortSerializer(serializers.ModelSerializer):
    """
    Project serializer that includes only the date fields for evaluation's representation of a project.
    """

    class Meta:
        model = Project
        fields = ('period_start', 'period_end')


class EvaluationSerializer(serializers.ModelSerializer):
    """
    """
    shopper_repr = ShopperSerializer(source='shopper', read_only=True)
    questionnaire_script_repr = QuestionnaireScriptSerializer(source='questionnaire_script', read_only=True)
    questionnaire = QuestionnaireSerializer(required=False)
    company_element_repr = CompanyElementSerializer(source='company_element', read_only=True)
    project_repr = ProjectShortSerializer(source='project', read_only=True)
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
        queryset = queryset.select_related('shopper__user', 'entity__city', 'questionnaire',
                                           'questionnaire_template', 'section')
        queryset = queryset.prefetch_related('questionnaire__blocks__questions__question_choices',
                                             'entity__employees__company',
                                             'entity__managers__user',
                                             'entity__sections__managers',
                                             'entity__sections__employees',
                                             'section__managers',
                                             'section__employees__company')
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

    def _copy_questionnaire_from_request(self, questionnaire_from_request, questionnaire_template):
        questionnaire = questionnaire_from_request
        questionnaire['template'] = questionnaire_template.id
        for block in questionnaire['blocks']:
            block['template_block'] = block['template_block'].id
            for question in block['questions']:
                self._check_if_indicator_question_has_null_score(question)
                question['template_question'] = question['template_question'].id
        return questionnaire

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


class ProjectStatisticsForCompanySerializer(serializers.ModelSerializer):
    """
        Serializer for company view that will contain only time,
        date and places/people to asses
    """
    company_element_repr = CompanyElementSerializer(source='company_element', read_only=True)

    class Meta:
        model = Evaluation
        fields = ('id', 'time_accomplished', 'company_element', 'company_element_repr')


class ProjectStatisticsForTenantSerializer(serializers.ModelSerializer):
    """
        Serializer for tenant view that will contain only time,
        date and places/people to asses and collector information
    """
    company_element_repr = CompanyElementSerializer(source='company_element', read_only=True)
    shopper_repr = ShopperSerializer(source='shopper', read_only=True)

    class Meta:
        model = Evaluation
        fields = ('id', 'time_accomplished', 'section', 'entity', 'entity_repr', 'company_element', 'company_element_repr', 'section_repr', 'shopper_repr')
