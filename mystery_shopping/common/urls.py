from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from .views import CountryViewSet
from .views import CountryRegionViewSet
from .views import CountyViewSet
from .views import CityViewSet
from .views import SectorViewSet
from .views import LocalityCsvUploadView


router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'countryregions', CountryRegionViewSet)
router.register(r'counties', CountyViewSet)
router.register(r'cities', CityViewSet)
router.register(r'sectors', SectorViewSet)

urlpatterns = [
    url(r'^upload/localities/$', LocalityCsvUploadView.as_view(), name='upload-localities')
]
