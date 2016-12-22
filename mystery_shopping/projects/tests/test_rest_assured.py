import json
from decimal import Decimal
from datetime import datetime

from rest_assured.testcases import CreateAPITestCaseMixin
from rest_assured.testcases import BaseRESTAPITestCase

from mystery_shopping.questionnaires.models import Questionnaire

from mystery_shopping.questionnaires.serializers import QuestionnaireTemplateSerializer
from mystery_shopping.projects.serializers import EvaluationSerializer
from mystery_shopping.projects.constants import EvaluationStatus

from mystery_shopping.factories.questionnaires import QuestionnaireTemplateStatusFactory
from mystery_shopping.factories.projects import EvaluationFactory
from mystery_shopping.factories.projects import EvaluationAssessmentLevelFactory
from mystery_shopping.factories.tenants import TenantFactory
from mystery_shopping.factories.users import UserThatIsTenantProductManagerFactory, UserFactory


# ToDo: make dates 'aware'


class EvaluationAPITestCase(CreateAPITestCaseMixin, BaseRESTAPITestCase):
    base_name = 'evaluation'
    factory_class = EvaluationFactory
    user_factory = UserThatIsTenantProductManagerFactory

    def get_create_data(self):
        self.data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.object.project.id,
            'shopper': self.object.shopper.id,
            'saved_by_user': self.object.saved_by_user.id,
            'questionnaire_script': self.object.questionnaire_script.id,
            'questionnaire_template': self.object.questionnaire_template.id,
            'entity': self.object.entity.id,
            'evaluation_assessment_level': None
        }
        return self.data

    def test_create(self, data=None, **kwargs):
        kwargs['format'] = 'json'
        super(EvaluationAPITestCase, self).test_create(data, **kwargs)

    def test_questionnaire_score_100(self):
        file = open('mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json')
        template_questionnaire_json_data = json.load(file)
        template_questionnaire_json = template_questionnaire_json_data[2]
        tenant = TenantFactory()
        created_by = UserFactory()
        status = QuestionnaireTemplateStatusFactory()
        template_questionnaire_json['tenant'] = tenant.id
        template_questionnaire_json['created_by'] = created_by.id
        template_questionnaire_json['status'] = status.id
        template_questionnaire_ser = QuestionnaireTemplateSerializer(data=template_questionnaire_json)
        template_questionnaire_ser.is_valid(raise_exception=True)
        template_questionnaire_ser.save()

        evaluation_data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.object.project.id,
            'shopper': self.object.shopper.id,
            'saved_by_user': self.object.saved_by_user.id,
            'questionnaire_script': self.object.questionnaire_script.id,
            'questionnaire_template': template_questionnaire_ser.instance.id,
            'entity': self.object.entity.id,
            'evaluation_assessment_level': None
        }
        evaluation_ser = EvaluationSerializer(data=evaluation_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()

        questionnaire = Questionnaire.objects.get(pk=evaluation_ser.data['questionnaire']['id'])
        for question in questionnaire.questions.all():
            for question_choice in question.question_choices.all():
                # Select all questions with 'positive' score
                if question_choice.text in {'A', 'Adevar', 'Yes'}:
                    question.answer_choices = [question_choice.id]
                    question.save()


        # Get updated evaluation
        evaluation_ser = EvaluationSerializer(evaluation_ser.instance)
        for block in evaluation_ser.data['questionnaire']['blocks']:
            for question in block['questions']:
                question['question_id'] = question['id']
        import copy
        # create an editable copy
        eval_data = copy.deepcopy(evaluation_ser.data)
        eval_data['status'] = EvaluationStatus.SUBMITTED

        evaluation_ser = EvaluationSerializer(evaluation_ser.instance, data=eval_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()
        file.close()
        self.assertEqual(Decimal(evaluation_ser.data['questionnaire']['score']), Decimal(100))

    def test_questionnaire_score_75(self):
        file = open('mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json')
        template_questionnaire_json_data = json.load(file)
        template_questionnaire_json = template_questionnaire_json_data[2]
        tenant = TenantFactory()
        created_by = UserFactory()
        status = QuestionnaireTemplateStatusFactory()
        template_questionnaire_json['tenant'] = tenant.id
        template_questionnaire_json['created_by'] = created_by.id
        template_questionnaire_json['status'] = status.id
        template_questionnaire_ser = QuestionnaireTemplateSerializer(data=template_questionnaire_json)
        template_questionnaire_ser.is_valid(raise_exception=True)
        template_questionnaire_ser.save()

        evaluation_data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.object.project.id,
            'shopper': self.object.shopper.id,
            'saved_by_user': self.object.saved_by_user.id,
            'questionnaire_script': self.object.questionnaire_script.id,
            'questionnaire_template': template_questionnaire_ser.instance.id,
            'entity': self.object.entity.id,
            'evaluation_assessment_level': None
        }
        evaluation_ser = EvaluationSerializer(data=evaluation_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()
        questionnaire = Questionnaire.objects.get(pk=evaluation_ser.data['questionnaire']['id'])
        for question in questionnaire.questions.all():
            for question_choice in question.question_choices.all():
                # Select all questions with 'positive' score, except two of them
                if question_choice.text in {'B', 'Provocare', 'Yes'}:
                    question.answer_choices = [question_choice.id]
                    question.save()

        # Get updated evaluation
        evaluation_ser = EvaluationSerializer(evaluation_ser.instance)
        for block in evaluation_ser.data['questionnaire']['blocks']:
            for question in block['questions']:
                question['question_id'] = question['id']
        import copy
        # create an editable copy
        eval_data = copy.deepcopy(evaluation_ser.data)
        eval_data['status'] = EvaluationStatus.SUBMITTED

        evaluation_ser = EvaluationSerializer(evaluation_ser.instance, data=eval_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()
        file.close()
        self.assertEqual(Decimal(evaluation_ser.data['questionnaire']['score']), Decimal(75))

    def test_status_change_with_evaluation_ass_level(self):
        file = open('mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json')
        template_questionnaire_json_data = json.load(file)
        template_questionnaire_json = template_questionnaire_json_data[2]
        tenant = TenantFactory()
        created_by = UserFactory()
        status = QuestionnaireTemplateStatusFactory()
        template_questionnaire_json['tenant'] = tenant.id
        template_questionnaire_json['created_by'] = created_by.id
        template_questionnaire_json['status'] = status.id
        template_questionnaire_ser = QuestionnaireTemplateSerializer(data=template_questionnaire_json)
        template_questionnaire_ser.is_valid(raise_exception=True)
        template_questionnaire_ser.save()
        evaluation_assessment_level = EvaluationAssessmentLevelFactory(consultants=[])

        evaluation_data = {
            'evaluation_type': 'visit',
            'is_draft': False,
            'suggested_start_date': datetime(2008, 1, 1),
            'suggested_end_date': datetime(2016, 1, 1),
            'status': EvaluationStatus.PLANNED,
            'time_accomplished': None,
            'project': self.object.project.id,
            'shopper': self.object.shopper.id,
            'saved_by_user': self.object.saved_by_user.id,
            'questionnaire_script': self.object.questionnaire_script.id,
            'questionnaire_template': template_questionnaire_ser.instance.id,
            'entity': self.object.entity.id,
            'evaluation_assessment_level': evaluation_assessment_level.id
        }
        evaluation_ser = EvaluationSerializer(data=evaluation_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()

        questionnaire = Questionnaire.objects.get(pk=evaluation_ser.data['questionnaire']['id'])
        for question in questionnaire.questions.all():
            for question_choice in question.question_choices.all():
                # Select all questions with 'positive' score
                if question_choice.text in {'A', 'Adevar', 'Yes'}:
                    question.answer_choices = [question_choice.id]
                    question.save()


        # Get updated evaluation
        evaluation_ser = EvaluationSerializer(evaluation_ser.instance)
        for block in evaluation_ser.data['questionnaire']['blocks']:
            for question in block['questions']:
                question['question_id'] = question['id']
        import copy
        # create an editable copy
        eval_data = copy.deepcopy(evaluation_ser.data)
        eval_data['status'] = EvaluationStatus.APPROVED

        evaluation_ser = EvaluationSerializer(evaluation_ser.instance, data=eval_data)
        evaluation_ser.is_valid(raise_exception=True)
        evaluation_ser.save()

        self.assertEqual(evaluation_ser.data['status'], EvaluationStatus.APPROVED)
