from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from .views import NPSDashboard

urlpatterns = [
    url(r'^nps/$',
        NPSDashboard.as_view(),
        name='nps-general-score'),
]