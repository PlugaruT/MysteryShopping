from factory.declarations import SubFactory
from factory.django import DjangoModelFactory
from factory.helpers import post_generation

from mystery_shopping.factories.projects import EvaluationFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import Respondent, RespondentCase

class RespondentFactory(DjangoModelFactory):
    class Meta:
        model = Respondent

    evaluation = SubFactory(EvaluationFactory)


class RespondentCaseFactory(DjangoModelFactory):
    class Meta:
        model = RespondentCase

    respondent = SubFactory(RespondentFactory)
    responsible_user = SubFactory(UserFactory)

    @post_generation
    def follow_up_tags(self, create, tags, **kwargs):
        if not create:
            return
        if tags:
            self.follow_up_tags.add(*tags)

    @post_generation
    def issue_tags(self, create, tags, **kwargs):
        if not create:
            return
        if tags:
            self.issue_tags.add(*tags)

    @post_generation
    def solution_tags(self, create, tags, **kwargs):
        if not create:
            return
        if tags:
            self.solution_tags.add(*tags)
