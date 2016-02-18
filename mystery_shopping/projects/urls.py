from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import PlaceToAssessViewSet
from .views import ProjectViewSet
from .views import ResearchMethodologyViewSet
from .views import EvaluationViewSet
from .views import EvaluationPerProjectViewSet
from .views import EvaluationAssessmentLevelViewSet
from .views import EvaluationAssessmentCommentViewSet


router = DefaultRouter()
router.register(r'placestoassess', PlaceToAssessViewSet)
# router.register(r'projects', ProjectViewSet)
router.register(r'researchmethodologies', ResearchMethodologyViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'evaluationassessmentlevels', EvaluationAssessmentLevelViewSet)
router.register(r'evaluationassessmentcomments', EvaluationAssessmentCommentViewSet)

project_router_for_projects = DefaultRouter()
project_router_for_projects.register(r'projects', ProjectViewSet)

project_evaluation = NestedSimpleRouter(project_router_for_projects, r'projects', lookup='project')
project_evaluation.register(r'evaluations', EvaluationPerProjectViewSet, base_name='project-evaluations')
