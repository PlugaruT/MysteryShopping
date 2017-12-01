from datetime import date, timedelta
from django.utils import timezone
from factory.django import DjangoModelFactory
from factory import SubFactory
from factory.fuzzy import FuzzyDate, FuzzyDateTime
from factory.fuzzy import FuzzyChoice
from factory import post_generation

from mystery_shopping.factories.companies import CompanyElementFactory
from mystery_shopping.factories.questionnaires import QuestionnaireFactory
from mystery_shopping.factories.users import UserFactory
from .tenants import TenantFactory

from .questionnaires import QuestionnaireScriptFactory
from .questionnaires import QuestionnaireTemplateFactory

from mystery_shopping.projects.models import ResearchMethodology
from mystery_shopping.projects.models import Project
from mystery_shopping.projects.constants import EvaluationStatus
from mystery_shopping.projects.models import Evaluation
from mystery_shopping.projects.models import EvaluationAssessmentLevel


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

    @post_generation
    def company_elements(self, create, company_elements, **kwargs):
        if not create:
            return
        if company_elements:
            for company_element in company_elements:
                self.company_elements.add(company_element)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    tenant = SubFactory(TenantFactory)
    company = SubFactory(CompanyElementFactory)
    project_manager = SubFactory(UserFactory)
    research_methodology = SubFactory(ResearchMethodologyFactory)
    detractors_manager = SubFactory(UserFactory)

    period_start = FuzzyDateTime(start_dt=timezone.now() - timedelta(days=100), end_dt=timezone.now())
    period_end = FuzzyDateTime(start_dt=timezone.now() - timedelta(days=100), end_dt=timezone.now())

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
    shopper = SubFactory(UserFactory)
    saved_by_user = SubFactory(UserFactory)
    questionnaire_script = SubFactory(QuestionnaireScriptFactory)
    questionnaire_template = SubFactory(QuestionnaireTemplateFactory)
    company_element = SubFactory(CompanyElementFactory)
    questionnaire = SubFactory(QuestionnaireFactory)

    # TODO: define evaluation choices in a separate file
    evaluation_type = FuzzyChoice(('call', 'visit'))
    is_draft = True
    suggested_start_date = date(2010, 6, 1)
    suggested_end_date = date(2011, 11, 2)
    status = EvaluationStatus.PLANNED
    time_accomplished = None


class EvaluationAssessmentLevelFactory(DjangoModelFactory):
    class Meta:
        model = EvaluationAssessmentLevel

    project = SubFactory(ProjectFactory)
    previous_level = None
    level = 0

    @post_generation
    def users(self, create, users, **kwargs):
        if not create:
            return
        if users:
            for user in users:
                self.users.add(user)
