from factory.django import DjangoModelFactory

from ..models import QuestionnaireTemplate, QuestionnaireTemplateBlock


class QuestionnaireTemplateFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplate

    title = "Factory Questionnaire Template title"


class QuestionnaireTemplateBlockFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateBlock

    title = "Factory Questionnaire Template Block title"
    weight = 1.0
