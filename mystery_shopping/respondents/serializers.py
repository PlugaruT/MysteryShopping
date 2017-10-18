from rest_framework import serializers

from mystery_shopping.questionnaires.serializers import QuestionnaireQuestionSerializer
from mystery_shopping.respondents.models import Respondent, RespondentCaseComment, RespondentCase
from mystery_shopping.users.serializers import UserSerializerGET


class RespondentForTenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Detractors for tenant (that included all the fields)
    """
    saved_by = UserSerializerGET(source='evaluation.saved_by_user', read_only=True)
    shopper = UserSerializerGET(source='evaluation.shopper', read_only=True)
    questionnaire_title = serializers.CharField(source='evaluation.questionnaire.title', read_only=True)
    time_accomplished = serializers.DateTimeField(source='evaluation.time_accomplished', read_only=True)
    questions = QuestionnaireQuestionSerializer(source='get_detractor_questions', many=True, read_only=True)
    visited_place = serializers.CharField(source='get_visited_place.element_name', read_only=True)

    class Meta:
        model = Respondent
        fields = '__all__'
        extra_kwargs = {
            'email': {
                'required': False
            },
            'phone': {
                'required': False
            }
        }

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('evaluation', 'evaluation__questionnaire')
        queryset = queryset.prefetch_related('evaluation__saved_by_user',
                                             'evaluation__shopper',
                                             'evaluation__questionnaire__blocks__questions__question_choices')
        return queryset


class RespondentForClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Detractors for clients (that exclude the saved_by field)
    """
    questionnaire_title = serializers.CharField(source='evaluation.questionnaire.title', read_only=True)
    time_accomplished = serializers.DateTimeField(source='evaluation.time_accomplished', read_only=True)
    questions = QuestionnaireQuestionSerializer(source='get_detractor_questions', many=True, read_only=True)
    visited_place = serializers.CharField(source='get_visited_place.element_name', read_only=True)

    class Meta:
        model = Respondent
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('evaluation', 'evaluation__questionnaire')
        queryset = queryset.prefetch_related('evaluation__saved_by_user',
                                             'evaluation__shopper',
                                             'evaluation__questionnaire__blocks__questions__question_choices')
        return queryset


class RespondentCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespondentCase
        fields = '__all__'


class RespondentCaseCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespondentCaseComment
        fields = '__all__'
