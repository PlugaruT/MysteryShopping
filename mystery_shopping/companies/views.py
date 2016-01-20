from rest_framework import viewsets
from rest_condition import Or

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

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultantViewOnly
from mystery_shopping.users.permissions import IsTenantConsultant


class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    # permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultantViewOnly),)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    # permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultantViewOnly),)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    # permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    # permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    # permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
