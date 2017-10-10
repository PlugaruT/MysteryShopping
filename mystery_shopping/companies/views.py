from django.db.models import F
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_condition import Or
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mystery_shopping.companies.models import AdditionalInfoType, CompanyElement, Industry, SubIndustry
from mystery_shopping.companies.serializers import (
    AdditionalInfoTypeSerializer,
    CompanyElementSerializer,
    IndustrySerializer,
    SimpleCompanyElementSerializer,
    SubIndustrySerializer
)
from mystery_shopping.companies.uploads import handle_csv_with_uploaded_sub_industries
from mystery_shopping.mystery_shopping_utils.models import TenantFilter
from mystery_shopping.users.permissions import (
    IsTenantConsultantViewOnly,
    IsTenantProductManager,
    IsTenantProjectManager
)

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
    serializer_class_companies = SimpleCompanyElementSerializer
    queryset = CompanyElement.objects.all()
    queryset = serializer_class.setup_eager_loading(queryset)
    filter_backends = (TenantFilter,)

    def create(self, request, *args, **kwargs):
        request.data['tenant'] = request.user.tenant.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(CompanyElement.tree.root_nodes())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            super(CompanyElementViewSet, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(data={'detail': 'TOAST.COMPANY_ELEMENT_USED_IN_EVALUATION'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def companies(self, request, *args, **kwargs):
        queryset = self.filter_queryset(CompanyElement.tree.root_nodes())
        serializer = self.serializer_class_companies(queryset, many=True)
        return Response(serializer.data)

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
        # sum 2 to the number of siblings because get_siblings() does not retrieve the element itself
        order_of_clone = element.get_siblings().count() + 2
        self.create_new_company_element(element, order_of_clone)
        self.clone_children(children)
        return Response(status=status.HTTP_201_CREATED)

    @detail_route(methods=['put'], url_path='change-order')
    def change_order(self, request, pk=None):
        """
        Detail view for changing the order of the element.
        :param request: Request that contains the new order of the element and the parent of the element
        :param pk: id of the element
        :return: status code 200
        """
        element = get_object_or_404(CompanyElement, pk=pk)
        new_order = request.data.get('order', element.order)
        new_parent = request.data.get('parent', element.parent)
        if element.parent_id == new_parent:
            self.change_order_of_siblings(element, new_order)
        else:
            self.change_order_if_parent_has_changed(element, new_order, new_parent)
        element.update_order(new_order)
        return Response(status=status.HTTP_200_OK)

    def change_order_if_parent_has_changed(self, element, new_order, new_parent):
        parent = get_object_or_404(CompanyElement, pk=new_parent)
        self.update_order_of_siblings_if_sibling_is_removed(element)
        element.update_parent(parent)
        self.change_order_of_siblings(element, new_order)

    def change_order_of_siblings(self, element, new_order):
        if element.order < new_order:
            self.update_order_if_new_order_greater_that_old_order(element, new_order)
        if element.order > new_order:
            self.update_order_if_new_order_less_that_old_order(element, new_order)

    def update_order_of_siblings_if_sibling_is_removed(self, element):
        siblings = element.get_siblings().filter(order__gt=element.order)
        self.decrease_order_by_one(siblings)

    def update_order_if_new_order_greater_that_old_order(self, element, new_order):
        siblings = element.get_siblings().filter(order__gt=element.order, order__lte=new_order)
        self.decrease_order_by_one(siblings)

    def update_order_if_new_order_less_that_old_order(self, element, new_order):
        siblings = element.get_siblings().filter(order__lt=element.order, order__gte=new_order)
        self.increase_order_by_one(siblings)

    @staticmethod
    def decrease_order_by_one(elements):
        CompanyElement.objects.filter(id__in=elements).update(order=F('order') - 1)

    @staticmethod
    def increase_order_by_one(elements):
        CompanyElement.objects.filter(id__in=elements).update(order=F('order') + 1)

    def clone_children(self, children):
        for child in children:
            new_children = child.children.all()
            self.create_new_company_element(child, child.order)
            if new_children.exists():
                self.clone_children(new_children)

    @staticmethod
    def create_new_company_element(element, order):
        element.id = None
        element.element_name = '{} {}'.format(element.element_name, '(copy)')
        element.order = order
        element.save()


class AdditionalInfoTypeViewSet(viewsets.ModelViewSet):
    """
    View for CRUD operations on AdditionalInfoType model
    """
    serializer_class = AdditionalInfoTypeSerializer
    queryset = AdditionalInfoType.objects.all()


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
