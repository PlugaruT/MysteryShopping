from rest_framework.routers import DefaultRouter

from mystery_shopping.questionnaires.views import BlockSimpleViewSet, CrossIndexTemplateViewSet, CrossIndexViewSet, \
    QuestionSimpleViewSet, QuestionnaireBlockViewSet, QuestionnaireQuestionChoiceViewSet, QuestionnaireQuestionViewSet, \
    QuestionnaireScriptViewSet, QuestionnaireSimpleViewSet, QuestionnaireTemplateBlockViewSet, \
    QuestionnaireTemplateQuestionChoiceViewSet, QuestionnaireTemplateQuestionViewSet, QuestionnaireTemplateViewSet, \
    QuestionnaireViewSet

router = DefaultRouter()
router.register(r'scripts', QuestionnaireScriptViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)
router.register(r'templatequestionnaires', QuestionnaireTemplateViewSet)
router.register(r'blocks', QuestionnaireBlockViewSet)
router.register(r'templateblocks', QuestionnaireTemplateBlockViewSet)
router.register(r'questions', QuestionnaireQuestionViewSet)
router.register(r'templatequestions', QuestionnaireTemplateQuestionViewSet)
router.register(r'templatequestionchoices', QuestionnaireTemplateQuestionChoiceViewSet)
router.register(r'questionchoices', QuestionnaireQuestionChoiceViewSet)
router.register(r'crossindextemplates', CrossIndexTemplateViewSet)
router.register(r'crossindexes', CrossIndexViewSet)
router.register(r'simplequestionnaires', QuestionnaireSimpleViewSet)
router.register(r'simplequestions', QuestionSimpleViewSet)
router.register(r'simpleblocks', BlockSimpleViewSet)
