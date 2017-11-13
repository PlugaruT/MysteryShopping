from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from mystery_shopping.common.views import CityViewSet, CountryCsvUploadView, CountryRegionViewSet, CountryViewSet, \
    CountyViewSet, LocalityCsvUploadView, SectorViewSet, TagsViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'countryregions', CountryRegionViewSet)
router.register(r'counties', CountyViewSet)
router.register(r'cities', CityViewSet)
router.register(r'sectors', SectorViewSet)
router.register(r'tags', TagsViewSet)

app_name = 'common'

urlpatterns = [
    url(r'^upload/localities/$', LocalityCsvUploadView.as_view(), name='upload-localities'),
    url(r'^upload/countries/$', CountryCsvUploadView.as_view(), name='upload-countries')
]
