import json

from django.test import TestCase

from .factories import QuestionnaireTemplateFactory, QuestionnaireTemplateBlockFactory
from ..models import QuestionnaireTemplateQuestion, QuestionnaireTemplateBlock, QuestionnaireTemplate
from ..serializers import QuestionnaireTemplateQuestionSerializer, QuestionnaireTemplateBlockSerializer, QuestionnaireTemplateSerializer


def _create_template_question(self, question):
    question_data = question['data']
    question_data['questionnaire_template'] = self.questionnaire_template.id
    question_data['template_block'] = self.questionnaire_template_block.id
    template_question = QuestionnaireTemplateQuestionSerializer(data=question_data)
    template_question.is_valid(raise_exception=True)
    template_question.save()
    self.assertEqual(QuestionnaireTemplateQuestion.objects.count(), 1)


def _create_template_block(self, block):
    block_data = block['data']
    block_data['questionnaire_template'] = self.questionnaire_template.id
    template_block = QuestionnaireTemplateBlockSerializer(data=block_data)
    template_block.is_valid(raise_exception=True)
    template_block.save()
    self.assertEqual(QuestionnaireTemplateBlock.objects.count(), 1)


def _create_questionnaire_template(self, questionnaire):
    questionnaire_data = questionnaire['data']
    questionnaire_template = QuestionnaireTemplateSerializer(data=questionnaire_data)
    questionnaire_template.is_valid(raise_exception=True)
    questionnaire_template.save()
    self.assertEqual(QuestionnaireTemplate.objects.count(), 1)


def make_method(func, content):

    def test_input(self):
        func(self, content)

    test_input.__name__ = 'test_{func}_{content}'.format(func=func.__name__, content=content['test_name'])
    return test_input


def generate(func, inputs):
    """
    Take a TestCase and add a test method for each input
    """
    def decorator(klass):
        for content in inputs:
            test_input = make_method(func, content)
            setattr(klass, test_input.__name__, test_input)
        return klass

    return decorator


@generate(_create_template_question, json.load(
    open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateQuestions.json")))
class QuestionnaireTemplateQuestionSerializerTestCase(TestCase):
    def setUp(self):
        self.questionnaire_template = QuestionnaireTemplateFactory()
        self.questionnaire_template_block = QuestionnaireTemplateBlockFactory(
            questionnaire_template=self.questionnaire_template)


@generate(_create_template_block, json.load(
    open("mystery_shopping/questionnaires/tests/QuestionnaireTemplateBlocks.json")))
class QuestionnaireTemplateBlockSerializerTestCase(TestCase):
    def setUp(self):
        self.questionnaire_template = QuestionnaireTemplateFactory()


@generate(_create_questionnaire_template, json.load(
    open("mystery_shopping/questionnaires/tests/QuestionnaireTemplates.json")))
class QuestionnaireTemplateSerializerTestCase(TestCase):
    pass
