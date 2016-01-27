from rest_framework import serializers

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation
from .models import PlaceToAssess

from mystery_shopping.users.models import TenantProductManager
from mystery_shopping.users.models import TenantProjectManager
from mystery_shopping.users.models import TenantConsultant

from mystery_shopping.companies.models import Entity
from mystery_shopping.companies.models import Section
from mystery_shopping.companies.serializers import EntitySerializer
from mystery_shopping.companies.serializers import SectionSerializer

from mystery_shopping.companies.serializers import CompanySerializer

from mystery_shopping.questionnaires.serializers import QuestionnaireScriptSerializer
from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.users.serializers import ShopperSerializer
from mystery_shopping.users.serializers import ProjectWorkerSerializer
from mystery_shopping.users.serializers import PersonToAssessSerializer
from mystery_shopping.users.serializer_fields import ProjectManagerRelatedField
from mystery_shopping.users.serializer_fields import ClientUserRelatedField

from mystery_shopping.users.serializers import TenantProductManagerSerializer
from mystery_shopping.users.serializers import TenantProjectManagerSerializer
from mystery_shopping.users.serializers import TenantConsultantSerializer


class PlaceToAssessSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = PlaceToAssess
        fields = '__all__'

    def to_representation(self, instance):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if instance.place_type.model == 'entity':
            to_serialize = Entity.objects.get(pk=instance.project_worker_id)
            serializer = EntitySerializer(to_serialize)
        elif instance.place_type.model == 'section':
            to_serialize = Section.objects.get(pk=instance.place_id)
            serializer = SectionSerializer(to_serialize)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class ResearchMethodologySerializer(serializers.ModelSerializer):
    """

    """
    scripts_repr = QuestionnaireScriptSerializer(source='scripts', many=True, read_only=True)
    questionnaires_repr = QuestionnaireTemplateSerializer(source='questionnaires', many=True, read_only=True)
    places_to_assess_repr = PlaceToAssessSerializer(source='places_to_assess', many=True, read_only=True)
    people_to_assess_repr = PersonToAssessSerializer(source='people_to_assess', many=True, read_only=True)
    project_id = serializers.IntegerField(required=False)

    class Meta:
        model = ResearchMethodology
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        project_id = validated_data.pop('project_id', None)

        scripts = validated_data.pop('scripts')
        questionnaires = validated_data.pop('questionnaires')
        places_to_assess = validated_data.pop('places_to_assess')
        people_to_assess = validated_data.pop('people_to_assess')

        print(validated_data)

        research_methodology = ResearchMethodology.objects.create(**validated_data)

        for script in scripts:
            research_methodology.scripts.add(script)

        for questionnaire in questionnaires:
            research_methodology.questionnaires.add(questionnaire)

        for place_to_assess in places_to_assess:
            research_methodology.places_to_assess.add(place_to_assess)

        for person_to_assess in people_to_assess:
            research_methodology.people_to_assess.add(person_to_assess)

        if project_id:
            project_to_set = Project.objects.filter(pk=project_id).first()

            if project_to_set:
                project_to_set.research_methodology = research_methodology
                project_to_set.save()

        return research_methodology


class ProjectSerializer(serializers.ModelSerializer):
    """

    """
    client_repr = CompanySerializer(source='client', read_only=True)
    shoppers_repr = ShopperSerializer(source='shoppers', many=True, read_only=True)
    project_manager_repr = ProjectManagerRelatedField(source='project_manager_object', read_only=True)
    consultants_repr = ProjectWorkerSerializer(source='consultants', many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class PlannedEvaluationSerializer(serializers.ModelSerializer):
    """

    """
    project_repr = ProjectSerializer(source='project', read_only=True)
    shopper_repr = ShopperSerializer(source='shopper', read_only=True)
    questionnaire_script_repr = QuestionnaireScriptSerializer(source='questionnaire_script', read_only=True)
    questionnaire_template_repr = QuestionnaireTemplateSerializer(source='questionnaire_template', read_only=True)
    entity_repr = EntitySerializer(source='entity', read_only=True)
    section_repr = SectionSerializer(source='section', read_only=True)
    employee_ser = ClientUserRelatedField(source='employee', read_only=True)
    
    class Meta:
        model = PlannedEvaluation
        fields = '__all__'

    def validate(self, data):
        # Check if number of maximum evaluations isn't surpassed
        if PlannedEvaluation.objects.filter(project=data['project']).count() >= Project.objects.get(pk=data['project'].id).research_methodology.number_of_evaluations:
            raise serializers.ValidationError('Number of evaluations is exceeded')
        else:
            return data


class AccomplishedEvaluationsSerializer(PlannedEvaluationSerializer):
    """

    """
    class Meta:
        model = AccomplishedEvaluation
        fields = '__all__'
