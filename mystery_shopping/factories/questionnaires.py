from django.utils import timezone
from factory import SubFactory, fuzzy
from factory.django import DjangoModelFactory

from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.questionnaires.constants import QuestionType
from mystery_shopping.questionnaires.models import CustomWeight, Questionnaire, QuestionnaireBlock, \
    QuestionnaireQuestion, QuestionnaireQuestionChoice, QuestionnaireScript, QuestionnaireTemplate, \
    QuestionnaireTemplateBlock, QuestionnaireTemplateQuestion, QuestionnaireTemplateQuestionChoice, \
    QuestionnaireTemplateStatus


class QuestionnaireScriptFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireScript

    title = "Questionnaire Script Factory"
    description = "Very fancy description"


class QuestionnaireTemplateStatusFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateStatus

    archived_date = timezone.now()
    archived_by = SubFactory(UserFactory)


class QuestionnaireTemplateFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplate

    tenant = SubFactory(TenantFactory)
    status = SubFactory(QuestionnaireTemplateStatusFactory)
    created_by = SubFactory(UserFactory)

    title = "Factory Questionnaire Template title"
    description = 'lalala'
    is_editable = True
    is_archived = False


class QuestionnaireTemplateBlockFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateBlock

    title = "Factory Questionnaire Template Block title"
    weight = 1.0
    order = 1
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)


class QuestionTemplateFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateQuestion

    question_body = 'Question From Factory'
    type = 's'
    order = 1
    weight = 10.0
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    template_block = SubFactory(QuestionnaireTemplateBlockFactory)


class QuestionnaireTemplateQuestionChoiceFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireTemplateQuestionChoice

    text = 'something here'
    order = 42
    template_question = SubFactory(QuestionTemplateFactory)


class QuestionnaireFactory(DjangoModelFactory):
    class Meta:
        model = Questionnaire

    title = "Factory Questionnaire Template title"
    template = SubFactory(QuestionnaireTemplateFactory)


class QuestionnaireBlockFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireBlock

    title = fuzzy.FuzzyText(length=10)
    weight = fuzzy.FuzzyDecimal(low=1, high=42)
    order = fuzzy.FuzzyInteger(low=2, high=42)
    questionnaire = SubFactory(QuestionnaireFactory)
    template_block = SubFactory(QuestionnaireTemplateBlockFactory)


class IndicatorQuestionFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireQuestion

    order = fuzzy.FuzzyInteger(low=1, high=42)
    weight = fuzzy.FuzzyDecimal(low=1, high=42)
    type = QuestionType.INDICATOR_QUESTION
    questionnaire = SubFactory(QuestionnaireFactory)
    template_question = SubFactory(QuestionTemplateFactory)
    block = SubFactory(QuestionnaireBlockFactory)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireQuestion

    order = fuzzy.FuzzyInteger(low=1, high=42)
    weight = fuzzy.FuzzyDecimal(low=1, high=42)
    type = QuestionType.SINGLE_CHOICE
    questionnaire = SubFactory(QuestionnaireFactory)
    template_question = SubFactory(QuestionTemplateFactory)
    block = SubFactory(QuestionnaireBlockFactory)


class ChoiceFactory(DjangoModelFactory):
    class Meta:
        model = QuestionnaireQuestionChoice

    question = SubFactory(QuestionFactory)
    order = fuzzy.FuzzyInteger(low=1, high=42)


class CustomWeightFactory(DjangoModelFactory):
    class Meta:
        model = CustomWeight

    question = SubFactory(QuestionFactory)
    name = fuzzy.FuzzyText(prefix='weight-', length=15)
