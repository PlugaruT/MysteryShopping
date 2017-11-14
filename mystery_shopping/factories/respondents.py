from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from mystery_shopping.factories.projects import EvaluationFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import RespondentCase, Respondent


class RespondentFactory(DjangoModelFactory):
    class Meta:
        model = Respondent

    evaluation = SubFactory(EvaluationFactory)


class RespondentCaseFactory(DjangoModelFactory):
    class Meta:
        model = RespondentCase

    respondent = SubFactory(RespondentFactory)
    responsible_user = SubFactory(UserFactory)