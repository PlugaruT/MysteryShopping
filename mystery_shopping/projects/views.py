from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or
from rest_condition import And

from openpyxl.writer.excel import save_virtual_workbook

from mystery_shopping.users.services import ShopperService
from .models import PlaceToAssess
from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment
from mystery_shopping.projects.constants import ProjectType
from .serializers import PlaceToAssessSerializer
from .serializers import ProjectSerializer
from .serializers import ResearchMethodologySerializer
from .serializers import EvaluationSerializer
from .serializers import EvaluationAssessmentLevelSerializer
from .serializers import EvaluationAssessmentCommentSerializer
from .serializers import ProjectStatisticsForCompanySerializer
from .serializers import ProjectStatisticsForTenantSerializer
from .spreadsheets import EvaluationSpreadsheet

from mystery_shopping.users.permissions import IsTenantProductManager, IsShopperAccountOwner
from mystery_shopping.users.permissions import HasReadOnlyAccessToProjectsOrEvaluations
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant
from mystery_shopping.users.permissions import IsShopper
from mystery_shopping.users.permissions import HasAccessToProjectsOrEvaluations


class PlaceToAssessViewSet(viewsets.ModelViewSet):
    queryset = PlaceToAssess.objects.all()
    serializer_class = PlaceToAssessSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get_queryset(self):
        """Filter queryset based on Project type ('c' or by default 'm') and according
        to the Tenant the current user belongs to.
        """
        queryset = self.queryset.all()
        project_type = self.request.query_params.get('type', 'm')
        project_type = project_type[0] if isinstance(project_type, list) else project_type
        queryset = queryset.filter(type=project_type)
        # queryset = self.get_serializer_class().setup_eager_loading(queryset)
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset

    @list_route(permission_classes=(IsShopperAccountOwner,), methods=['get'])
    def collectorevaluations(self, request):
        """A view to return a list of projects, which has places (entities or sections) paired up with their corresponding
        questionnaires.

        The view serves calls from Customer Experience Index project and returns the
        list of available entities with all the required information to fill in a
        questionnaire and create a realized evaluation.

        :returns: List of projects with place and questionnaire data.
        :rtype: list
        """
        available_list_of_places = list()
        if request.user.is_collector():
            shopper_service = ShopperService(request.user.shopper)
            available_list_of_places = shopper_service.get_available_list_of_places_with_questionnaires()

        return Response(available_list_of_places, status=status.HTTP_200_OK)


class ProjectPerCompanyViewSet(viewsets.ViewSet):
    queryset = Project.objects.all()
    permission_classes = (And(IsAuthenticated, Or(HasAccessToProjectsOrEvaluations, HasReadOnlyAccessToProjectsOrEvaluations)),)

    def list(self, request, company_pk=None):
        project_type = self.request.query_params.get('type', 'm')
        project_type = project_type[0] if isinstance(project_type, list) else project_type
        queryset = self.queryset.filter(company=company_pk, type=project_type,
                                        tenant=self.request.user.tenant)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, pk=None, company_pk=None):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, company_pk=None):
        queryset = self.queryset.filter(pk=pk, company=company_pk)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def update(self, request, pk=None, company_pk=None):
        request.data['research_methodology']['tenant'] = request.user.tenant.pk
        queryset = self.queryset.filter(pk=pk, company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResearchMethodologyViewSet(viewsets.ModelViewSet):
    queryset = ResearchMethodology.objects.all()
    serializer_class = ResearchMethodologySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager),)

    def get_queryset(self):
        queryset = ResearchMethodology.objects.all()
        queryset = queryset.filter(tenant=self.request.user.tenant)
        return queryset


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)

    def get_queryset(self):
        queryset = Evaluation.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        if self.request.user.user_type in ['tenantproductmanager', 'tenantprojectmanager', 'tenantconsultant']:
            queryset = queryset.filter(project__tenant=self.request.user.tenant)
        elif self.request.user.user_type is 'shopper':
            queryset = queryset.filter(shopper__user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        self._if_not_mystery_and_evaluations_left_raise_error(request.data, project_id, 1)
        self._set_saved_by_user(request.user, request.data)
        evaluation = self._create_evaluations(request)
        return Response(evaluation, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def many(self, request, *args, **kwargs):
        project_id = request.data[0].get('project')
        self._if_not_mystery_and_evaluations_left_raise_error(request.data, project_id, len(request.data))
        self._set_saved_by_user_many(request.user, request.data)
        evaluations = self._create_evaluations(request, True)
        return Response(evaluations, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def get_excel(self, request, pk=None):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = "attachment; filename=test.xlsx"
        instance = Evaluation.objects.get(pk=pk)
        evaluation_spreadsheet = EvaluationSpreadsheet(evaluation=instance)
        response.write(save_virtual_workbook(evaluation_spreadsheet.generate_spreadsheet()))
        return response

    def _is_mystery_project(self, project_id):
        return Project.objects.get_project_type(project_id) == ProjectType.MYSTERY_SHOPPING

    def _enough_evaluations_available(self, is_many, data, project_id):
        evaluations_left = self._get_remaining_number_of_evaluations(project_id)
        evaluations_to_create = len(data) if is_many else 1
        return evaluations_to_create < evaluations_left

    def _get_remaining_number_of_evaluations(self, project_id):
        total_number_of_evaluations = Project.objects.get(pk=project_id).research_methodology.number_of_evaluations
        current_number_of_evaluations = Evaluation.objects.filter(project=project_id).count()
        return total_number_of_evaluations - current_number_of_evaluations

    def _create_evaluations(self, request, is_many=False):
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def _if_not_mystery_and_evaluations_left_raise_error(self, data, project_id, number_to_create):
        are_evaluations_left = self._get_remaining_number_of_evaluations(project_id) >= number_to_create
        if self._is_mystery_project(project_id) and not are_evaluations_left:
            raise ValidationError('Number of evaluations exceeded.')

    def _set_saved_by_user(self, user, data):
        data['saved_by_user'] = user.id

    def _set_saved_by_user_many(self, user, evaluations):
        for evaluation in evaluations:
            self._set_saved_by_user(user, evaluation)


class EvaluationPerShopperViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, shopper_pk=None):
        queryset = Evaluation.objects.filter(shopper=shopper_pk)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, shopper_pk=None):
        evaluation = get_object_or_404(Evaluation, pk=pk, shopper=shopper_pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)


class EvaluationPerProjectViewSet(viewsets.ViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        for_assessment = request.query_params.get('forAssessment', None)
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        if for_assessment:
            if request.user.user_type == 'tenantconsultant':
                queryset = queryset.filter(evaluation_assessment_level__consultants__in=[request.user.user_type_attr])
            elif request.user.user_type == 'tenantprojectmanager':
                queryset = queryset.filter(evaluation_assessment_level__project_manager=request.user.user_type_attr)
            else:
                queryset = Evaluation.objects.none()

        queryset = self.serializer_class.setup_eager_loading(queryset)
        serializer = EvaluationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, pk=None, company_pk=None, project_pk=None):
        is_many = True if isinstance(request.data, list) else False
        project_id = request.data[0]['project'] if is_many else request.data['project']
        total_number_of_evaluations = Project.objects.get(pk=project_id).research_methodology.number_of_evaluations
        current_number_of_evaluations = Evaluation.objects.filter(project=project_id).count()
        evaluations_left = total_number_of_evaluations - current_number_of_evaluations
        evaluations_to_create = len(request.data) if is_many else 1
        project_type = Project.objects.get_project_type(project_id)
        if evaluations_to_create > evaluations_left and project_type == ProjectType.MYSTERY_SHOPPING:
            raise ValidationError('Number of evaluations exceeded. Left: {}.'.format(evaluations_left))

        serializer = EvaluationSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        queryset = self.serializer_class.setup_eager_loading(queryset)
        evaluation = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, evaluation)
        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data)

    def update(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        serializer = EvaluationSerializer(evaluation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, company_pk=None, project_pk=None):
        queryset = Evaluation.objects.filter(pk=pk, project=project_pk, project__company=company_pk)
        evaluation = get_object_or_404(queryset, pk=pk)
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EvaluationAssessmentLevelViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentLevel.objects.all()
    serializer_class = EvaluationAssessmentLevelSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class EvaluationAssessmentCommentViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAssessmentComment.objects.all()
    serializer_class = EvaluationAssessmentCommentSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant, IsShopper),)


class ProjectStatisticsForCompanyViewSet(viewsets.ViewSet):
    serializer_class = ProjectStatisticsForCompanySerializer
    permission_classes = (IsAuthenticated, HasReadOnlyAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        for_assessment = request.query_params.get('forAssessment', None)
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        if for_assessment:
            if request.user.user_type == 'tenantconsultant':
                queryset = queryset.filter(evaluation_assessment_level__consultants__in=[request.user.user_type_attr])
            elif request.user.user_type == 'tenantprojectmanager':
                queryset = queryset.filter(evaluation_assessment_level__project_manager=request.user.user_type_attr)
            else:
                queryset = Evaluation.objects.none()

        serializer = ProjectStatisticsForCompanySerializer(queryset, many=True)
        return Response(serializer.data)


class ProjectStatisticsForTenantViewSet(viewsets.ViewSet):
    serializer_class = ProjectStatisticsForTenantSerializer
    permission_classes = (IsAuthenticated, HasAccessToProjectsOrEvaluations,)

    def list(self, request, company_pk=None, project_pk=None):
        for_assessment = request.query_params.get('forAssessment', None)
        queryset = Evaluation.objects.filter(project=project_pk, project__company=company_pk)
        if for_assessment:
            if request.user.user_type == 'tenantconsultant':
                queryset = queryset.filter(evaluation_assessment_level__consultants__in=[request.user.user_type_attr])
            elif request.user.user_type == 'tenantprojectmanager':
                queryset = queryset.filter(evaluation_assessment_level__project_manager=request.user.user_type_attr)
            else:
                queryset = Evaluation.objects.none()

        serializer = ProjectStatisticsForTenantSerializer(queryset, many=True)
        return Response(serializer.data)
