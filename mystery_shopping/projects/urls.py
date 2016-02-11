from rest_framework.routers import DefaultRouter

from .views import PlaceToAssessViewSet
from .views import ProjectViewSet
from .views import ResearchMethodologyViewSet
from .views import PlannedEvaluationViewSet
from .views import AccomplishedEvaluationViewSet
from .views import EvaluationAssessmentLevelViewSet

router = DefaultRouter()
router.register(r'placestoassess', PlaceToAssessViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'researchmethodologies', ResearchMethodologyViewSet)
router.register(r'plannedevaluations', PlannedEvaluationViewSet)
router.register(r'accomplishedevaluations', AccomplishedEvaluationViewSet)
router.register(r'evaluationassessmentlevels', EvaluationAssessmentLevelViewSet)
