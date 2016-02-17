from rest_framework.routers import DefaultRouter

from .views import PlaceToAssessViewSet
from .views import ProjectViewSet
from .views import ResearchMethodologyViewSet
from .views import EvaluationViewSet
from .views import EvaluationAssessmentLevelViewSet
from .views import EvaluationAssessmentCommentViewSet


router = DefaultRouter()
router.register(r'placestoassess', PlaceToAssessViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'researchmethodologies', ResearchMethodologyViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'evaluationassessmentlevels', EvaluationAssessmentLevelViewSet)
router.register(r'evaluationassessmentcomments', EvaluationAssessmentCommentViewSet)
