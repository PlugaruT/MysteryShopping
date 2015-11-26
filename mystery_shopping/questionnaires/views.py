from rest_framework import viewsets

from .models import QuestionnaireScript, QuestionnaireTemplate, QuestionnaireTemplateBlock, QuestionnaireTemplateQuestion
from .serializers import QuestionnaireScriptSerializer, QuestionnaireTemplateSerializer, QuestionnaireTemplateBlockSerializer, QuestionnaireTemplateQuestionSerializer


class QuestionnaireScriptViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireScript.objects.all()
    serializer_class = QuestionnaireScriptSerializer


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.all()
    serializer_class = QuestionnaireTemplateSerializer


class QuestionnaireTemplateBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateBlock.objects.all()
    serializer_class = QuestionnaireTemplateBlockSerializer


class QuestionnaireTemplateQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestion.objects.all()
    serializer_class = QuestionnaireTemplateQuestionSerializer