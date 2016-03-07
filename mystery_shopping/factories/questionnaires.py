from factory.django import DjangoModelFactory
from factory import SubFactory

from mystery_shopping.questionnaires.models import QuestionnaireScript
from mystery_shopping.questionnaires.models import QuestionnaireTemplate
from mystery_shopping.questionnaires.models import QuestionnaireTemplateBlock
from mystery_shopping.questionnaires.models import QuestionnaireTemplateQuestion
from mystery_shopping.factories.tenants import TenantFactory


class QuestionnaireScriptFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireScript

    title = "Questionnaire Script Factory"
    description = "Very fancy description"


class QuestionnaireTemplateFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplate

    tenant = SubFactory(TenantFactory)
    title = "Factory Questionnaire Template title"
    description = 'lalala'
    is_editable = True


class QuestionnaireTemplateBlockFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateBlock

    title = "Factory Questionnaire Template Block title"
    weight = 1.0
    order = 1
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)


class QuestionnaireTemplateQuestionFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateQuestion

    question_body = 'Question From Factory'
    type = 's'
    order = 1
    weight = 10.0
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    template_block = SubFactory(QuestionnaireTemplateBlockFactory)
