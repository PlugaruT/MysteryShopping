from django.http.response import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from mystery_shopping.projects.constants import ProjectType
from mystery_shopping.projects.models import Evaluation, Project
from mystery_shopping.projects.serializers import EvaluationSerializer
from mystery_shopping.projects.spreadsheets import EvaluationSpreadsheet


class EvaluationViewMixIn:
    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        self._if_not_evaluations_left_raise_error(project_id)
        self._set_saved_by_user(request.user, request.data)
        evaluation = self._create_evaluations(request.data)
        return Response(evaluation, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def many(self, request, *args, **kwargs):
        project_id = request.data[0].get('project')
        self._if_not_evaluations_left_raise_error(project_id, len(request.data))
        self._set_saved_by_user_many(request.user, request.data)
        evaluations = self._create_evaluations(request.data, True)
        return Response(evaluations, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def get_excel(self, request, pk=None):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "attachment; filename=test.xlsx"
        instance = Evaluation.objects.get(pk=pk)
        evaluation_spreadsheet = EvaluationSpreadsheet(evaluation=instance)
        response.write(save_virtual_workbook(evaluation_spreadsheet.generate_spreadsheet()))
        return response

    def _get_remaining_number_of_evaluations(self, project_id):
        project = Project.objects.get(pk=project_id)
        total_number_of_evaluations = project.get_total_number_of_evaluations()
        current_number_of_evaluations = Evaluation.objects.filter(project=project_id).count()
        return total_number_of_evaluations - current_number_of_evaluations

    def _create_evaluations(self, data, is_many=False):
        serializer = EvaluationSerializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def _if_not_evaluations_left_raise_error(self, project_id, number_to_create=1):
        are_evaluations_left = self._get_remaining_number_of_evaluations(project_id) >= number_to_create
        if not are_evaluations_left:
            raise ValidationError('Number of evaluations exceeded.')

    def _set_saved_by_user(self, user, data):
        data['saved_by_user'] = user.id

    def _set_saved_by_user_many(self, user, evaluations):
        for evaluation in evaluations:
            self._set_saved_by_user(user, evaluation)
