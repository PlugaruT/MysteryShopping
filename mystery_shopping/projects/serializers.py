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
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.users.serializers import ShopperSerializer
from mystery_shopping.users.serializers import PersonToAssessSerializer
from mystery_shopping.users.serializers import TenantProjectManagerSerializer
from mystery_shopping.users.serializers import TenantConsultantSerializer
from mystery_shopping.users.serializer_fields import TenantUserRelatedField
from mystery_shopping.users.serializer_fields import ClientUserRelatedField

from mystery_shopping.users.models import PersonToAssess
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
    scripts_repr = QuestionnaireScriptSerializer(source='scripts', many=True, read_only=True)
    questionnaires_repr = QuestionnaireTemplateSerializer(source='questionnaires', many=True, read_only=True)
    places_to_assess_repr = PlaceToAssessSerializer(source='places_to_assess', many=True, required=False)
    people_to_assess_repr = PersonToAssessSerializer(source='people_to_assess', many=True, required=False)
    project_id = serializers.IntegerField(required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts', [])
        questionnaires = validated_data.pop('questionnaires', [])
        places_to_assess = validated_data.pop('places_to_assess', [])
        people_to_assess = validated_data.pop('people_to_assess', [])

        print(validated_data)

        research_methodology = ResearchMethodology.objects.create(**validated_data)

        for script in scripts:
            research_methodology.scripts.add(script)

        for questionnaire in questionnaires:
            research_methodology.questionnaires.add(questionnaire)

        for place_to_assess in places_to_assess:
            place_to_assess['research_methodology'] = research_methodology
            place_to_assess_instance = PlaceToAssess.objects.create(**place_to_assess)
            research_methodology.places_to_assess.add(place_to_assess_instance)

        for person_to_assess in people_to_assess:
            person_to_assess['research_methodology'] = research_methodology
            person_to_assess_instance = PersonToAssess.objects.create(**person_to_assess)
            research_methodology.people_to_assess.add(person_to_assess_instance)

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

        for script in scripts:
            instance.scripts.add(script)

        for questionnaire in questionnaires:
            instance.questionnaires.add(questionnaire)

        for place_to_assess in places_to_assess:
            place_to_assess['research_methodology'] = instance
            place_to_assess_instance = PlaceToAssess.objects.create(**place_to_assess)
            instance.places_to_assess.add(place_to_assess_instance)

        for person_to_assess in people_to_assess:
            person_to_assess['research_methodology'] = instance
            person_to_assess_instance = PersonToAssess.objects.create(**person_to_assess)
            instance.people_to_assess.add(person_to_assess_instance)

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
        print(validated_data)
        research_methodology = validated_data.pop('research_methodology', None)
        consultants = validated_data.pop('consultants', [])
        validated_data.pop('shoppers', None)

        project = Project.objects.create(**validated_data)

        for consultant in consultants:
            project.consultants.add(consultant)

        # if project_workers is not None:
        #     for project_worker in project_workers:
        #         project_worker['project'] = project
        #         ProjectWorker.objects.create(**project_worker)

        # TODO refactor this method according to the one in .update() method
        if research_methodology is not None:
            research_methodology['project_id'] = project.id
            research_methodology_ser = ResearchMethodology(data=research_methodology)
            research_methodology_ser.is_valid(raise_exeption=True)
            research_methodology_ser.save()

        return project

    def update(self, instance, validated_data):
        print(validated_data)
        consultants = validated_data.pop('consultants', [])
        research_methodology = validated_data.pop('research_methodology', None)

        instance.prepare_for_update()

        for consultant in consultants:
            instance.consultants.add(consultant)

        # if project_workers is not None:
        #     for project_worker in project_workers:
        #         project_worker['project'] = instance
        #         ProjectWorker.objects.create(**project_worker)

        if research_methodology is not None:
            research_methodology_instance = instance.research_methodology
            research_methodology['project_id'] = instance.id

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
    entity_repr = EntitySerializer(source='entity', read_only=True)
    section_repr = SectionSerializer(source='section', read_only=True)
    employee_repr = ClientUserRelatedField(source='employee', read_only=True)

    class Meta:
        model = Evaluation
        fields = '__all__'

    def validate(self, data):
        # Check if number of maximum evaluations isn't surpassed
        if Evaluation.objects.filter(project=data['project']).count() >= Project.objects.get(pk=data['project'].id).research_methodology.number_of_evaluations:
            raise serializers.ValidationError('Max number of evaluations is exceeded')
        else:
            return data
