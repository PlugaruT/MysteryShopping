from factory.django import DjangoModelFactory
from factory import SubFactory
from factory import post_generation
from factory.fuzzy import FuzzyText
from factory.fuzzy import FuzzyChoice

from mystery_shopping.cxi.models import CodedCause
from mystery_shopping.cxi.models import CodedCauseLabel
from mystery_shopping.factories.tenants import TenantFactory


class CodedCauseLabelFactory(DjangoModelFactory):
    class Meta:
        model = CodedCauseLabel

    tenant = SubFactory(TenantFactory)
    name = FuzzyChoice((1, 2, 3))


class CodedCauseFactory(DjangoModelFactory):
    class Meta:
        model = CodedCause

    tenant = SubFactory(TenantFactory)
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
