from datetime import date

from factory.django import DjangoModelFactory
from factory import SubFactory
from factory.fuzzy import FuzzyDate
from factory.fuzzy import FuzzyChoice
from factory import post_generation

from .companies import CompanyFactory
from .tenants import TenantFactory

from .users import TenantProjectManagerFactory
from .users import TenantProjectManagerFactory
from .users import ShopperFactory
from .questionnaires import QuestionnaireScriptFactory
from .questionnaires import QuestionnaireTemplateFactory
from .companies import EntityFactory
from .companies import SectionFactory

from mystery_shopping.projects.models import ResearchMethodology
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.project_statuses import ProjectStatus
from mystery_shopping.projects.models import Evaluation


class ResearchMethodologyFactory(DjangoModelFactory):
    class Meta:
        model = ResearchMethodology

    tenant = SubFactory(TenantFactory)
    number_of_evaluations = 5
    description = 'basic research meth description.'

    @post_generation
    def scripts(self, create, scripts, **kwargs):
        if not create:
            return
        if scripts:
            for script in scripts:
                self.scripts.add(script)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    tenant = SubFactory(TenantFactory)
    company = SubFactory(CompanyFactory)
    project_manager = SubFactory(TenantProjectManagerFactory)
    research_methodology = SubFactory(ResearchMethodologyFactory)

    period_start = FuzzyDate(date(1990, 12, 12))
    period_end = FuzzyDate(date(2000, 11, 2))

    @post_generation
    def consultants(self, create, consultants, **kwargs):
        if not create:
            return
        if consultants:
            for consultant in consultants:
                self.consultants.add(consultant)

    @post_generation
    def shoppers(self, create, shoppers, **kwargs):
        if not create:
            return
        if shoppers:
            for shopper in shoppers:
                self.shoppers.add(shopper)


class EvaluationFactory(DjangoModelFactory):
    class Meta:
        model = Evaluation

    project = SubFactory(ProjectFactory)
    shopper = SubFactory(ShopperFactory)
    questionnaire_script = SubFactory(QuestionnaireScriptFactory)
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    entity = SubFactory(EntityFactory)

    section = None
    employee = None
    questionnaire = None

    # TODO: define evaluation choices in a separate file
    evaluation_type = FuzzyChoice(('call', 'visit'))
    is_draft = True
    suggested_start_date = FuzzyDate(date(1990, 12, 12))
    suggested_end_date = FuzzyDate(date(2000, 11, 2))
    # status = FuzzyChoice(ProjectStatus.PLANNED, ProjectStatus.DRAFT,
    #                      ProjectStatus.SUBMITTED, ProjectStatus.REVIEWED,
    #                      ProjectStatus.APPROVED, ProjectStatus.DECLINED,
    #                      ProjectStatus.REJECTED,)
    status = ProjectStatus.PLANNED
    time_accomplished = None
