from collections import defaultdict

from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.response import Response
from rest_condition import Or

from .algorithms import group_questions_by_answer
from .algorithms import get_nps_marks
from .algorithms import calculate_indicator_score
from .models import CodedCauseLabel
from .models import CodedCause
from .serializers import CodedCauseLabelSerializer
from .serializers import CodedCauseSerializer

from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.projects.models import Project

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager


class CodedCauseLabelViewSet(viewsets.ModelViewSet):
    queryset = CodedCauseLabel.objects.all()
    serializer_class = CodedCauseLabelSerializer


class CodedCauseViewSet(viewsets.ModelViewSet):
    queryset = CodedCause.objects.all()
    serializer_class = CodedCauseSerializer


# Rename View
class NPSDashboard(views.APIView):

    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', None)
        indicator_type = request.query_params.get('indicator', None)
        response = dict()
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                # I only get the first questionnaire_template from the research methodology
                # as each research methodology for a Customer Experience Index Project has
                # only one questionnaire template
                questionnaire_template = project.research_methodology.questionnaires.first()

                indicator_dict = get_nps_marks(questionnaire_template)
                indicator_score = calculate_indicator_score(indicator_dict['scores'])

                response['general'] = dict()
                # response['general']['indicator_type'] = 'NPS Question'
                response['general']['score'] = indicator_score

                nps_categories = group_questions_by_answer(questionnaire_template, indicator_type)
                response['details'] = list()

                # Todo: move this into function
                for item_label, responses in nps_categories.items():
                    detail_item = dict()
                    detail_item['results'] = list()

                    for answer_choice in responses:
                        answer_choice_result = dict()
                        answer_choice_result['choice'] = answer_choice
                        answer_choice_result['score'] = calculate_indicator_score(responses[answer_choice])
                        answer_choice_result['number_of_respondents'] = len(responses[answer_choice])
                        detail_item['results'].append(answer_choice_result)

                    detail_item['item_label'] = item_label
                    response['details'].append(detail_item)

                return Response(response, status.HTTP_200_OK)
            except Project.DoesNotExist:
                return Response({'detail': 'No Project with this id exists'},
                                status.HTTP_404_NOT_FOUND)

        return Response({
            'detail': 'Project was not provided'
        }, status.HTTP_400_BAD_REQUEST)