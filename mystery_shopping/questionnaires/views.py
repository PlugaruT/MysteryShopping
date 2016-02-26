from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_condition import Or

from .models import QuestionnaireScript
from .models import Questionnaire
from .models import QuestionnaireTemplate
from .models import QuestionnaireBlock
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireQuestion
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireQuestionChoice
from .models import QuestionnaireTemplateQuestionChoice
from .serializers import QuestionnaireScriptSerializer
from .serializers import QuestionnaireSerializer
from .serializers import QuestionnaireTemplateSerializer
from .serializers import QuestionnaireBlockSerializer
from .serializers import QuestionnaireTemplateBlockSerializer
from .serializers import QuestionnaireQuestionSerializer
from .serializers import QuestionnaireTemplateQuestionSerializer
from .serializers import QuestionnaireQuestionChoiceSerializer
from .serializers import QuestionnaireTemplateQuestionChoiceSerializer

from mystery_shopping.users.permissions import IsTenantProductManager
from mystery_shopping.users.permissions import IsTenantProjectManager
from mystery_shopping.users.permissions import IsTenantConsultant


class QuestionnaireScriptViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireScript.objects.all()
    serializer_class = QuestionnaireScriptSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplate.objects.all()
    serializer_class = QuestionnaireTemplateSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)

    def get_queryset(self):
        queryset = Questionnaire.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class QuestionnaireTemplateBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateBlock.objects.all()
    serializer_class = QuestionnaireTemplateBlockSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireBlockViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireBlock.objects.all()
    serializer_class = QuestionnaireBlockSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestion.objects.all()
    serializer_class = QuestionnaireTemplateQuestionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestion.objects.all()
    serializer_class = QuestionnaireQuestionSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireTemplateQuestionChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireTemplateQuestionChoice.objects.all()
    serializer_class = QuestionnaireTemplateQuestionChoiceSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)


class QuestionnaireQuestionChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireQuestionChoice.objects.all()
    serializer_class = QuestionnaireQuestionChoiceSerializer
    permission_classes = (Or(IsTenantProductManager,  IsTenantProjectManager, IsTenantConsultant),)
