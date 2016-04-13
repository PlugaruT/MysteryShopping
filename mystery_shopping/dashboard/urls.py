from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from .views import DashboardTemplateView
from .views import DashboardCommentViewSet


router = DefaultRouter()
router.register(r'templates', DashboardTemplateView)
router.register(r'comments', DashboardCommentViewSet)
