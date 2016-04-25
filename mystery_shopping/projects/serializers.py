from collections import OrderedDict

from rest_framework import serializers

from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import PlaceToAssess
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment

from mystery_shopping.companies.models import Entity
from mystery_shopping.companies.models import Section
from mystery_shopping.companies.serializers import EntitySerializer
from mystery_shopping.companies.serializers import SectionSerializer

from mystery_shopping.companies.serializers import CompanySerializer

from mystery_shopping.questionnaires.serializers import QuestionnaireScriptSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.questionnaires.models import QuestionnaireQuestion, QuestionnaireScript
from mystery_shopping.questionnaires.models import Questionnaire
from mystery_shopping.users.serializers import ShopperSerializer
from mystery_shopping.users.serializers import PersonToAssessSerializer
from mystery_shopping.users.serializers import TenantProjectManagerSerializer
from mystery_shopping.users.serializers import TenantConsultantSerializer
from mystery_shopping.users.serializer_fields import TenantUserRelatedField
from mystery_shopping.users.serializer_fields import ClientUserRelatedField
from mystery_shopping.projects.constants import ProjectStatus

from mystery_shopping.users.models import PersonToAssess
from mystery_shopping.users.models import Shopper
from mystery_shopping.users.models import TenantConsultant


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
        extra_kwargs = {'consultants': {'allow_empty': True, 'many': True}}


class PlaceToAssessSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = PlaceToAssess
        fields = '__all__'
        extra_kwargs = {'research_methodology': {'required': False}}

    def to_representation(self, instance):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if instance.place_type.model == 'entity':
            to_serialize = Entity.objects.get(pk=instance.place_id)
            serializer = EntitySerializer(to_serialize)
        elif instance.place_type.model == 'section':
            to_serialize = Section.objects.get(pk=instance.place_id)
            serializer = SectionSerializer(to_serialize)
        else:
            raise Exception('Unexpected type of tagged object')

        place_to_assess_dict = {
            'place_type': instance.place_type_id,
            'place_id': instance.place_id
        }

        place_to_assess_dict.update(serializer.data)

        return place_to_assess_dict


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """

    """
    scripts = serializers.PrimaryKeyRelatedField(queryset=QuestionnaireScript.objects.all(), required=False, many=True)
    scripts_repr = QuestionnaireScriptSerializer(source='scripts', many=True, read_only=True)
    questionnaires_repr = QuestionnaireTemplateSerializer(source='questionnaires', many=True, read_only=True)
    places_to_assess_repr = PlaceToAssessSerializer(source='places_to_assess', many=True, required=False)
    people_to_assess_repr = PersonToAssessSerializer(source='people_to_assess', many=True, required=False)
    project_id = serializers.IntegerField(required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'

    def create(self, validated_data):
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts', [])
        questionnaires = validated_data.pop('questionnaires', [])
        places_to_assess = validated_data.pop('places_to_assess', [])
        people_to_assess = validated_data.pop('people_to_assess', [])

        research_methodology = ResearchMethodology.objects.create(**validated_data)

        research_methodology.scripts.set(scripts)
        research_methodology.questionnaires.set(questionnaires)

        places_to_set = list()
        for place_to_assess in places_to_assess:
            place_to_assess['research_methodology'] = research_methodology
            places_to_set.append(PlaceToAssess.objects.create(**place_to_assess))
        research_methodology.places_to_assess.set(places_to_set)

        people_to_set = list()
        for person_to_assess in people_to_assess:
            person_to_assess['research_methodology'] = research_methodology
            people_to_set.append(PersonToAssess.objects.create(**person_to_assess))
        research_methodology.people_to_assess.set(people_to_set)

        if project_id:
            project_to_set = Project.objects.filter(pk=project_id).first()

            if project_to_set:
                project_to_set.research_methodology = research_methodology
                project_to_set.save()

        return research_methodology

    def update(self, instance, validated_data):
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts', [])
        questionnaires = validated_data.pop('questionnaires', [])
        places_to_assess = validated_data.pop('places_to_assess', [])
        people_to_assess = validated_data.pop('people_to_assess', [])

        instance.prepare_for_update()

        instance.scripts.set(scripts)
        instance.questionnaires.set(questionnaires)

        places_to_set = list()
        for place_to_assess in places_to_assess:
            place_to_assess['research_methodology'] = instance
            places_to_set.append(PlaceToAssess.objects.create(**place_to_assess))
        instance.places_to_assess.set(places_to_set)

        people_to_set = list()
        for person_to_assess in people_to_assess:
            person_to_assess['research_methodology'] = instance
            people_to_set.append(PersonToAssess.objects.create(**person_to_assess))
        instance.people_to_assess.set(people_to_set)

        if project_id:
            project_to_set = Project.objects.filter(pk=project_id).first()

            if project_to_set:
                project_to_set.research_methodology = instance
                project_to_set.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ProjectSerializer(serializers.ModelSerializer):
    """

    """
    company_repr = CompanySerializer(source='company', read_only=True)
    shoppers_repr = ShopperSerializer(source='shoppers', many=True, read_only=True)
    project_manager_repr = TenantProjectManagerSerializer(source='project_manager', read_only=True)
    research_methodology = ResearchMethodologySerializer(required=False)
    shoppers = serializers.PrimaryKeyRelatedField(queryset=Shopper.objects.all(), many=True, allow_null=True, required=False)
    consultants_repr = TenantConsultantSerializer(source='consultants', read_only=True, many=True)
    evaluation_assessment_levels_repr = EvaluationAssessmentLevelSerializer(source='evaluation_assessment_levels', read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'

    # @staticmethod
    # def setup_eager_loading(queryset):
    #     """
    #     Perform necessary eager loading of data.
    #     """
    #     # queryset = queryset.select_related()
    #     queryset = queryset.prefetch_related('company__departments__entities__sections', 'shoppers__user', 'research_methodology__scripts', 'research_methodology__questionnaires',
    #     'research_methodology__questionnaires__template_blocks','research_methodology__questionnaires__template_blocks__template_questions' )
    #     # queryset = queryset.prefetch_related(None)
    #     return queryset

    def create(self, validated_data):
        research_methodology = validated_data.pop('research_methodology', None)
        consultants = validated_data.pop('consultants', [])
        validated_data.pop('shoppers', None)

        project = Project.objects.create(**validated_data)

        project.consultants.set(consultants)

        if research_methodology is not None:
            research_methodology['project_id'] = project.id
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
            research_methodology['questionnaires'] = list(map(lambda x: x.id, research_methodology.get('questionnaires', [])))

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
                research_methodology_ser = ResearchMethodologySerializer(research_methodology_instance, data=research_methodology)
            else:
                research_methodology_ser = ResearchMethodologySerializer(data=research_methodology)
            research_methodology_ser.is_valid(raise_exception=True)
            research_methodology_ser.save()
            instance.research_methodology = research_methodology_ser.instance

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class EvaluationSerializer(serializers.ModelSerializer):
    """
    """
    shopper_repr = ShopperSerializer(source='shopper', read_only=True)
    questionnaire_script_repr = QuestionnaireScriptSerializer(source='questionnaire_script', read_only=True)
    questionnaire = QuestionnaireSerializer(required=False)
    entity_repr = EntitySerializer(source='entity', read_only=True)
    section_repr = SectionSerializer(source='section', read_only=True)
    employee_repr = ClientUserRelatedField(source='employee', read_only=True)

    class Meta:
        model = Evaluation
        fields = '__all__'

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
        if validated_data.get('type', 'm') == 'm':
            questionnaire_template_serialized = QuestionnaireTemplateSerializer(questionnaire_template)
            questionnaire_to_create = OrderedDict(questionnaire_template_serialized.data)
            questionnaire_to_create['blocks'] = questionnaire_to_create.pop('template_blocks')
            for block in questionnaire_to_create['blocks']:
                block['template_block'] = block.get('id')
                block['order_number'] = block.pop('id')
                block['parent_order_number'] = block.pop('parent_block')
                block['questions'] = block.pop('template_questions')
                for question in block['questions']:
                    question['template_question'] = question.pop('id')
                    question['question_choices'] = question.pop('template_question_choices')

        else:
            questionnaire_to_create = validated_data.get('questionnaire', None)

        questionnaire_to_create['template'] = questionnaire_template.id
        questionnaire_to_create_ser = QuestionnaireSerializer(data=questionnaire_to_create)
        questionnaire_to_create_ser.is_valid(raise_exception=True)
        questionnaire_to_create_ser.save()
        validated_data['questionnaire'] = questionnaire_to_create_ser.instance

        evaluation = Evaluation.objects.create(**validated_data)
        return evaluation

    def update(self, instance, validated_data):
        current_status = instance.status
        questionnaire = validated_data.pop('questionnaire', None)

        if questionnaire and current_status in ProjectStatus.EDITABLE_STATUSES:
            for block in questionnaire.get('blocks', []):
                for question in block.get('questions', []):
                    question_instance = QuestionnaireQuestion.objects.get(questionnaire=question.get('questionnaire'), pk=question.get('question_id'))
                    question_instance.answer = question.get('answer', None)
                    question_instance.answer_choices = question.get('answer_choices', [])
                    question_instance.comment = question.get('comment', None)
                    question_instance.save()

            # After updating only the questions above, the updates are not taken
            # into account when returning the serialized evaluation instance. This
            # is probably (I didn't investigate it a lot) because the evaluation's
            # cache does not know that its questionnaire instance was changed and
            # it uses the cached instance. For it to use the updated questionnaire
            # representation, resubmit the questionnaire to the evaluation.
            instance.questionnaire = Questionnaire.objects.get(pk=instance.questionnaire.pk)
            instance.questionnaire.save()

            if validated_data.get('status', ProjectStatus.PLANNED) == ProjectStatus.PLANNED:
                instance.status = ProjectStatus.DRAFT
            else:
                instance.status = validated_data.get('status')

            if validated_data.get('status', None) == ProjectStatus.SUBMITTED:
                instance.questionnaire.calculate_score()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
