from django.test import TestCase
import json

from .factories import QuestionnaireTemplateFactory, QuestionnaireTemplateBlockFactory
from ..models import QuestionnaireTemplateQuestion, QuestionnaireTemplate
from ..serializers import QuestionnaireTemplateQuestionSerializer


def _create(self, question):
    question_data = question['data']

    question_data['questionnaire_template'] = self.questionnaire_template.id
    question_data['template_block'] = self.questionnaire_template_block.id
    template_question = QuestionnaireTemplateQuestionSerializer(data=question_data)
    template_question.is_valid(raise_exception=True)
    template_question.save()
    self.assertEqual(QuestionnaireTemplateQuestion.objects.count(), 1)


def make_method(func, question):

    def test_input(self):
        func(self, question)

    test_input.__name__ = 'test_{func}_{input}'.format(func=func.__name__, input=question['test_name'])
    return test_input


def generate(func, inputs):
    """
    Take a TestCase and add a test method for each input
    """
    def decorator(klass):
        for question in inputs:
            test_input = make_method(func, question)
            setattr(klass, test_input.__name__, test_input)
        return klass

    return decorator


@generate(_create, json.load(open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateQuestions.json")))
class QuestionnaireTemplateQuestionSerializerTestCase(TestCase):
    def setUp(self):
        self.questionnaire_template = QuestionnaireTemplateFactory()
        self.questionnaire_template_block = QuestionnaireTemplateBlockFactory(
            questionnaire_template=self.questionnaire_template)
