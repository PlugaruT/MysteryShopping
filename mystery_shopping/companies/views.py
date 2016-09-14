from rest_framework import viewsets
from rest_condition import Or
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mystery_shopping.companies.models import SubIndustry
from mystery_shopping.companies.serializers import SubIndustrySerializer
from mystery_shopping.companies.uploads import handle_csv_with_uploaded_sub_industries
from .models import Industry
from .models import Company
from .models import Department
from .models import Entity
from .models import Section

from .serializers import IndustrySerializer
from .serializers import CompanySerializer
from .serializers import DepartmentSerializer
from .serializers import EntitySerializer
from .serializers import SectionSerializer
from mystery_shopping.users.serializers import SimpleCompanySerializer

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultantViewOnly
from mystery_shopping.users.permissions import IsTenantConsultant


class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultantViewOnly),)


class SubIndustryViewSet(viewsets.ModelViewSet):
    queryset = SubIndustry.objects.all()
    serializer_class = SubIndustrySerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultantViewOnly),)


class IndustryCsvUploadView(APIView):
    """
        A view for uploading a .csv with all the localities to the platform.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, *args, **kwargs):

        csv_file = request.data.get('file', None)

        if csv_file.content_type == 'text/csv':
            handle_csv_with_uploaded_sub_industries(csv_file)

            return Response({
                'message': 'File uploaded successfully!'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'details': 'File type is not .csv'
            }, status=status.HTTP_400_BAD_REQUEST)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    simple_serializer_class = SimpleCompanySerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultantViewOnly),)

    def get_serializer_class(self):
        if self.request.query_params.get('simple', False):
            return self.simple_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        queryset = Company.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(CompanyViewSet, self).create(request, *args, **kwargs)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Department.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(DepartmentViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        at_least_one_manager_has_evaluations = all([manager.has_evaluations() for manager in instance.get_managers()])
        at_least_one_entity_has_evaluations = all([entity.has_evaluations() for entity in instance.get_entities()])

        if at_least_one_manager_has_evaluations or at_least_one_entity_has_evaluations:
            return Response({"You can not delete thisjnkljnkl object"}, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Entity.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(EntityViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        at_least_one_manager_has_evaluations = all([manager.has_evaluations() for manager in instance.get_managers()])
        at_least_one_employee_has_evaluations = all([employee.has_evaluations() for employee in instance.get_employees()])
        at_least_one_section_has_evaluations = all([section.has_evaluations() for section in instance.get_sections()])

        if at_least_one_manager_has_evaluations or at_least_one_employee_has_evaluations or at_least_one_section_has_evaluations:
            return Response({"You can not delete this object"}, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Section.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(SectionViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        at_least_one_manager_has_evaluations = all([manager.has_evaluations() for manager in instance.get_managers()])
        at_least_one_employee_has_evaluations = all([employee.has_evaluations() for employee in instance.get_employees()])

        if at_least_one_manager_has_evaluations or at_least_one_employee_has_evaluations:
            return Response({"You can not delete this object"}, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

