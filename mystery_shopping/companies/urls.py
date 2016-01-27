from rest_framework.routers import DefaultRouter

from .views import IndustryViewSet
from .views import CompanyViewSet
from .views import DepartmentViewSet
from .views import EntityViewSet
from .views import SectionViewSet


router = DefaultRouter()
router.register(r'industries', IndustryViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'entities', EntityViewSet)
router.register(r'sections', SectionViewSet)
