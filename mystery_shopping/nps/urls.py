from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .views import CodedCauseLabelViewSet
from .views import CodedCauseViewSet
from .views import IndicatorDashboard


router = DefaultRouter()
router.register(r'codedcauselabels', CodedCauseLabelViewSet)
router.register(r'codedcauses', CodedCauseViewSet)

urlpatterns = [
    url(r'^nps/$',
        IndicatorDashboard.as_view(),
        name='nps-general-score'),
]