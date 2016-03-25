from collections import defaultdict

from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response
from rest_condition import Or

from .algorithms import group_questions_by_answer
from .algorithms import get_nps_marks
from .algorithms import calculate_indicator_score
from .algorithms import get_indicator_details
from .models import CodedCauseLabel
from .models import CodedCause
from .serializers import CodedCauseLabelSerializer
from .serializers import CodedCauseSerializer

from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.projects.models import Project
from mystery_shopping.questionnaires.models import Questionnaire

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    serializer_class = CodedCauseSerializer


# Rename View
class IndicatorDashboard(views.APIView):

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        indicator_type = request.query_params.get('indicator', None)
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                # I only get the first questionnaire_template from the research methodology
                # as each research methodology for a Customer Experience Index Project has
                # only one questionnaire template
                questionnaire_template = project.research_methodology.questionnaires.first()
                questionnaire_list = Questionnaire.objects.get_project_questionnaires(questionnaire_template, project)

                response = dict()
                response['general'] = dict()

                indicator_list = get_nps_marks(questionnaire_list, indicator_type)
                response['general']['score'] = calculate_indicator_score(indicator_list)

                response['details'] = get_indicator_details(questionnaire_list, indicator_type)

                return Response(response, status.HTTP_200_OK)
            except Project.DoesNotExist:
                return Response({'detail': 'No Project with this id exists'},
                                status.HTTP_404_NOT_FOUND)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)