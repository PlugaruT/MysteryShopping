from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_condition import Or
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mystery_shopping.companies.models import SubIndustry, CompanyElement
from mystery_shopping.companies.serializers import SubIndustrySerializer, CompanyElementSerializer
from mystery_shopping.companies.uploads import handle_csv_with_uploaded_sub_industries
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
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
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultantViewOnly),)


class SubIndustryViewSet(viewsets.ModelViewSet):
    """
    View for CompanyElement models. The view will list only elements with parent=None of the form:
    ```
    {
        "id": object_id,
        "element_name": "element_name",
        "element_type": "element_type",
        "children": [] # list of childrens of the same type,
        "additional_info": {}, # some additional fields stored in a dict
        "parent": 4 # id of the parent element
    }
    ```
    """
    queryset = SubIndustry.objects.all()
    serializer_class = SubIndustrySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultantViewOnly),)


class CompanyElementViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyElementSerializer
    queryset = CompanyElement.objects.root_nodes()
    queryset = serializer_class.setup_eager_loading(queryset)
    filter_backends = (TenantFilter,)

    @detail_route(methods=['post'])
    def clone(self, request, pk=None):
        """
        Detail view for cloning a CompanyElement. The view will clone all children's of the instance appending to
        strings 'copy'
        :param request: Request that contains additional info
        :param pk: id of the root element to be cloned
        :return: status code 201
        """
        element = get_object_or_404(CompanyElement, pk=pk)
        children = element.children.all()
        self.create_new_company_element(element)
        self.clone_children(children)
        return Response(status=status.HTTP_201_CREATED)

    def clone_children(self, children):
        for child in children:
            new_children = child.children.all()
            self.create_new_company_element(child)
            if new_children.exists():
                self.clone_children(new_children)

    @staticmethod
    def create_new_company_element(element):
        element.id = None
        element.element_name = '{} {}'.format(element.element_name, '(copy)')
        element.save()


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



# ToDo: remove this
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    simple_serializer_class = SimpleCompanySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultantViewOnly),)

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
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Department.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(DepartmentViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.has_evaluations():
            return Response({"You can not delete this object because some subdivisions have evaluations applied"},
                            status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Entity.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(EntityViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_evaluations():
            return Response({"You can not delete this object because some subdivisions have evaluations applied"},
                            status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (Or(IsTenantProductManager, IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Section.objects.filter(tenant=self.request.user.tenant)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.pk
        return super(SectionViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.has_evaluations():
            return Response({"You can not delete this object because some subdivisions have evaluations applied"},
                            status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# till here.
