from rest_framework import status
from rest_framework import views
from rest_framework.response import Response

from .algorithms import get_nps_marks
from .algorithms import calculate_nps_score

from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.projects.models import Project


class NPSDashboard(views.APIView):

    def get(self, request, *args, **kwargs):
        questionnaire_template_id = request.query_params.get('questionnaire_template', None)
        project_id = request.query_params.get('project', None)

        if questionnaire_template_id and project_id:
            try:
                questionnaire_template = QuestionnaireTemplate.objects.get(id=questionnaire_template_id)

                nps_dict = get_nps_marks(questionnaire_template, int(project_id))
                nps_score, promoters_percentage, passives_percentage, detractors_percentage = calculate_nps_score(nps_dict['scores'])

                return Response({
                    'nps_score': nps_score
                }, status.HTTP_200_OK)
            except QuestionnaireTemplate.DoesNotExist:
                return Response({'details': 'No Questionnaire Template with this id exists'},
                                status.HTTP_404_NOT_FOUND)

        return Response({
            'details': 'Either a questionnaire template or a project were not provided'
        }, status.HTTP_400_BAD_REQUEST)