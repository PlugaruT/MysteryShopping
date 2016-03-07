import json
from decimal import Decimal
from datetime import datetime

from rest_assured.testcases import CreateAPITestCaseMixin
from rest_assured.testcases import ReadWriteRESTAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase
from factory.fuzzy import FuzzyDateTime

from mystery_shopping.questionnaires.models import Questionnaire

from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.projects.serializers import EvaluationSerializer
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

    def test_questionnaire_score_100(self):
        template_questionnaire_json_data = json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json"))
        template_questionnaire_json = template_questionnaire_json_data[2]
        tenant = TenantFactory()
        template_questionnaire_json['tenant'] = tenant.id
        template_questionnaire_ser = QuestionnaireTemplateSerializer(data=template_questionnaire_json)
        template_questionnaire_ser.is_valid(raise_exception=True)
        template_questionnaire_ser.save()

        evaluation_data = {
            "evaluation_type": "visit",
            "is_draft": False,
            "suggested_start_date": datetime(2008, 1, 1),
            "suggested_end_date": datetime(2016, 1, 1),
            "status": ProjectStatus.PLANNED,
            "time_accomplished": None,
            "project": self.object.project.id,
            "shopper": self.object.shopper.id,
            "questionnaire_script": self.object.questionnaire_script.id,
            "questionnaire_template": template_questionnaire_ser.instance.id,
            "entity": self.object.entity.id,
            "evaluation_assessment_level": None
        }
        evaluation_ser = EvaluationSerializer(data=evaluation_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()
        questionnaire = Questionnaire.objects.get(pk=evaluation_ser.data['questionnaire']['id'])
        for question in questionnaire.questions.all():
            for question_choice in question.question_choices.all():
                if question_choice.text in {'Da', 'A', 'Adevar', 'Yes'}:
                    question.answer_choices = [question_choice.id]
                    question.save()

        questionnaire.calculate_score()
        self.assertEqual(questionnaire.score, Decimal(100))
