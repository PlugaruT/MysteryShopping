from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import PlaceToAssessViewSet
from .views import ProjectViewSet
from .views import ResearchMethodologyViewSet
from .views import EvaluationViewSet
from .views import EvaluationPerProjectViewSet
from .views import EvaluationAssessmentLevelViewSet
from .views import EvaluationAssessmentCommentViewSet
from mystery_shopping.companies.urls import company_project_router


router = DefaultRouter()
router.register(r'placestoassess', PlaceToAssessViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'researchmethodologies', ResearchMethodologyViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'evaluationassessmentlevels', EvaluationAssessmentLevelViewSet)
router.register(r'evaluationassessmentcomments', EvaluationAssessmentCommentViewSet)

# Define another `projects` route that is a nested route of `companies` route. Do this because there is a need
# to have both a nested router within `companies` route AND a default router for `projects` to obtain the list
# of all project for a tenant.
project_evaluation = NestedSimpleRouter(company_project_router, r'projects', lookup='project')
project_evaluation.register(r'evaluations', EvaluationPerProjectViewSet, base_name='project-evaluations')
