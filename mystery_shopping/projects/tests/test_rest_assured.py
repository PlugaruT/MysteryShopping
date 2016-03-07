import json
from datetime import datetime

from rest_assured.testcases import CreateAPITestCaseMixin
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase
from factory.fuzzy import FuzzyDateTime

from mystery_shopping.questionnaires.serializers import QuestionnaireTemplate
from mystery_shopping.projects.project_statuses import ProjectStatus

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateFactory
from mystery_shopping.factories.projects import ProjectFactory
from mystery_shopping.factories.projects import EvaluationFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory


class EvaluationAPITestCase(CreateAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'evaluation'
    factory_class = EvaluationFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def get_create_data(self):

        self.data = {
            "evaluation_type": "visit",
            "is_draft": False,
            "suggested_start_date": datetime(2008, 1, 1),
            "suggested_end_date": datetime(2016, 1, 1),
            "status": ProjectStatus.PLANNED,
            "time_accomplished": None,
            "project": self.object.project.id,
            "shopper": self.object.shopper.id,
            "questionnaire_script": self.object.questionnaire_script.id,
            "questionnaire_template": self.object.questionnaire_template.id,
            "entity": self.object.entity.id,
            "evaluation_assessment_level": None
        }
        return self.data

    def test_create(self, data=None, **kwargs):
        kwargs['format'] = 'json'
        super(EvaluationAPITestCase, self).test_create(data, **kwargs)

    def _test_questionnaire_score_100(self):
        questionnaire_json = json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json"))
        tenant = TenantFactory()
        questionnaire_json['tenant'] = tenant.id
