from rest_framework import viewsets, permissions

from .models import QuestionnaireScript, QuestionnaireTemplate, QuestionnaireTemplateBlock, QuestionnaireTemplateQuestion
from .serializers import QuestionnaireScriptSerializer, QuestionnaireTemplateSerializer, QuestionnaireTemplateBlockSerializer, QuestionnaireTemplateQuestionSerializer


class QuestionnaireScriptViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireScript.objects.all()
    serializer_class = QuestionnaireScriptSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.all()
    serializer_class = QuestionnaireTemplateSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class QuestionnaireTemplateBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateBlock.objects.all()
    serializer_class = QuestionnaireTemplateBlockSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class QuestionnaireTemplateQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestion.objects.all()
    serializer_class = QuestionnaireTemplateQuestionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
