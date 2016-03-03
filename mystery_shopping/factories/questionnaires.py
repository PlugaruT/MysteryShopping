from factory.django import DjangoModelFactory
from factory import SubFactory

from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.questionnaires.models import QuestionnaireTemplateBlock
from mystery_shopping.factories.tenants import TenantFactory


class QuestionnaireTemplateFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplate

    tenant = SubFactory(TenantFactory)
    title = "Factory Questionnaire Template title"
    description = 'lalala'
    is_editable = True


class QuestionnaireTemplateBlockDefaultFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateBlock

    title = "Factory Questionnaire Template Block title"
    weight = 1.0
    order = 2
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    parent_block = None


class QuestionnaireTemplateBlockFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateBlock

    title = "Factory Questionnaire Template Block title"
    weight = 1.0
    order = 1
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    # parent_block = SubFactory(QuestionnaireTemplateBlockDefaultFactory)
