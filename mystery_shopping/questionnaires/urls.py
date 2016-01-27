from rest_framework.routers import DefaultRouter

from .views import QuestionnaireScriptViewSet
from .views import QuestionnaireTemplateViewSet
from .views import QuestionnaireViewSet
from .views import QuestionnaireTemplateBlockViewSet
from .views import QuestionnaireBlockViewSet
from .views import QuestionnaireTemplateQuestionViewSet
from .views import QuestionnaireQuestionViewSet


router = DefaultRouter()
router.register(r'scripts', QuestionnaireScriptViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)
router.register(r'templatequestionnaires', QuestionnaireTemplateViewSet)
router.register(r'blocks', QuestionnaireBlockViewSet)
router.register(r'templateblocks', QuestionnaireTemplateBlockViewSet)
router.register(r'questions', QuestionnaireQuestionViewSet)
router.register(r'templatequestions', QuestionnaireTemplateQuestionViewSet)
