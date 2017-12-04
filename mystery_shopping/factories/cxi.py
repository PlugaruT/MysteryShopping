from factory import SubFactory, post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText

from mystery_shopping.cxi.models import CodedCause, CodedCauseLabel, WhyCause
from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.questionnaires import QuestionFactory
from mystery_shopping.factories.tenants import TenantFactory


class CodedCauseLabelFactory(DjangoModelFactory):
    class Meta:
        model = CodedCauseLabel

    tenant = SubFactory(TenantFactory)
    name = FuzzyText(length=10)


class CodedCauseFactory(DjangoModelFactory):
    class Meta:
        model = CodedCause

    tenant = SubFactory(TenantFactory)
    project = SubFactory(ProjectFactory)
    coded_label = SubFactory(CodedCauseLabelFactory)
    type = FuzzyText(length=30)
    sentiment = FuzzyChoice(('a', 'f'))

    @post_generation
    def raw_causes(self, create, causes, **kwargs):
        if not create:
            return
        if causes:
            for cause in causes:
                self.raw_causes.add(cause)

    @post_generation
    def responsible_users(self, create, users, **kwargs):
        if not create:
            return
        if users:
            self.responsible_users.add(*users)


class WhyCauseFactory(DjangoModelFactory):
    class Meta:
        model = WhyCause

    answer = FuzzyText(length=20)
    question = SubFactory(QuestionFactory, related_name='why_causes')
    is_appreciation_cause = True
