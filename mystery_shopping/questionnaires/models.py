from decimal import Decimal

from django.db import models
from django.contrib.postgres.fields import ArrayField
from model_utils import Choices
from model_utils.models import TimeStampedModel

from mptt.models import MPTTModel, TreeForeignKey

from .constants import QuestionType
from .constants import IndicatorQuestionType as IndQuestType
from .managers import QuestionnaireQuerySet
from .managers import QuestionnaireQuestionQuerySet

from mystery_shopping.tenants.models import Tenant

# REMINDER: don't use newline characters in the representation


class QuestionnaireScript(models.Model):
    """

    """
    # Attributes
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return 'Title: %s,' \
               'description: %s' % (self.title, self.description[0:50])


class QuestionnaireAbstract(models.Model):
    """
    Abstract class for Questionnaire Template and Questionnaire.

    """
    # Attributes
    title = models.CharField(max_length=100)
    type_questionnaire = Choices(('m', 'Mystery Questionnaire'),
                                 ('c', 'Customer Experience Index Questionnaire'))
    type = models.CharField(max_length=1, choices=type_questionnaire, default=type_questionnaire.m)

    class Meta:
        abstract = True
        ordering = ('title',)


class QuestionnaireTemplate(QuestionnaireAbstract):
    """
    Templates for questionnaires that will not contain answers.

    """
    # Relations
    tenant = models.ForeignKey(Tenant)

    # Attributes
    description = models.TextField()
    is_editable = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return 'Title: {}'.format(self.title)

    def get_indicator_question(self, indicator_type):
        try:
            return self.template_questions.get(type=indicator_type)
        except:
            return None

    def archive(self):
        self.is_archived = True

    def unarchive(self):
        self.is_archived = False


class Questionnaire(TimeStampedModel, QuestionnaireAbstract):
    """
    The questionnaires that will contain answers.

    """
    # Relations
    template = models.ForeignKey(QuestionnaireTemplate)

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.PositiveSmallIntegerField(default=100)

    objects = models.Manager.from_queryset(QuestionnaireQuerySet)()

    class Meta:
        default_related_name = 'questionnaires'

    def __str__(self):
        return 'Title: {}'.format(self.title)

    def get_indicator_question(self, indicator_type):
        try:
            return self.questions.get(type=IndQuestType.INDICATOR_QUESTION, additional_info=indicator_type)
        except:
            return None

    def calculate_score_for_m(self):
        '''
        Function for calculating the score of a Mystery Shopping Questionnaire
        '''
        self.score = 0
        blocks = self.blocks.filter(parent_block=None)

        for block in blocks:
            self.score += block.calculate_score()

        self.save()

        return self.score

    def calculate_score_for_c(self):
        '''
        Function for making calculations on Customer Experience Index Questionnaires. (now it does nothing)
        '''
        pass

    def calculate_score(self):
        '''
        Function for determining what type of calculation to perform on the questionnaire taking into consideration the type
        '''
        self.score = getattr(self, 'calculate_score_for_{}'.format(self.type))()
        self.save()

    # def get_indicator_question(self, indicator_question_type):
    #     return self..question.get(type=indicator_question_type)


class QuestionnaireBlockAbstract(models.Model):
    """
    Abstract Questionnaire block for QuestionnaireBlockTemplate and QuestionnaireBlock

    """
    title = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField()

    class Meta:
        abstract = True


class QuestionnaireTemplateBlock(QuestionnaireBlockAbstract, MPTTModel):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate, related_name='template_blocks')
    parent_block = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        parent_attr = 'parent_block'

    def __str__(self):
        return 'Title: {}'.format(self.title)


class QuestionnaireBlock(QuestionnaireBlockAbstract, MPTTModel):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(Questionnaire, related_name='blocks')
    parent_block = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    template_block = models.ForeignKey(QuestionnaireTemplateBlock, related_name='blocks')

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class MPTTMeta:
        order_insertion_by = ('title',)
        parent_attr = 'parent_block'

    def __str__(self):
        return 'Title: {}'.format(self.title)

    def calculate_score(self):
        temp_score = Decimal(0)

        blocks = self.get_children()
        for block in blocks:
            temp_score += block.calculate_score()

        questions = self.questions.all()
        for question in questions:
            temp_score += question.calculate_score()

        self.score = (temp_score * self.weight) / 100
        self.save()

        return self.score


class QuestionAbstract(models.Model):
    """
    Abstract class for QuestionTemplate and Question

    """
    # Attributes
    question_body = models.CharField(max_length=200)  # TODO: find optimal length
    type_choices = Choices((QuestionType.TEXT_FIELD, 'Text Field'),
                           (QuestionType.DATE_FIELD, 'Date Field'),
                           (QuestionType.SINGLE_CHOICE, 'Single Choice'),
                           (QuestionType.MULTIPLE_CHOICE, 'Multiple Choice'),
                           (IndQuestType.INDICATOR_QUESTION, 'Indicator Question'))
    type = models.CharField(max_length=1, choices=type_choices, default=type_choices.t)
    max_score = models.PositiveSmallIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    show_comment = models.BooleanField(default=True)
    additional_info = models.CharField(max_length=30, blank=Tenant)

    class Meta:
        abstract = True
        ordering = ('question_body',)


class QuestionnaireTemplateQuestion(QuestionAbstract):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate)
    template_block = models.ForeignKey(QuestionnaireTemplateBlock)

    class Meta:
        default_related_name = 'template_questions'

    def __str__(self):
        return 'Question body: {}'.format(self.question_body)

    def prepare_to_update(self):
        self.template_question_choices.all().delete()


class QuestionnaireQuestion(QuestionAbstract):
    """

    """
    questionnaire = models.ForeignKey(Questionnaire)
    block = models.ForeignKey(QuestionnaireBlock)
    template_question = models.ForeignKey(QuestionnaireTemplateQuestion)

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    answer_choices = ArrayField(models.IntegerField(), null=True, blank=True)

    objects = models.Manager.from_queryset(QuestionnaireQuestionQuerySet)()

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return 'Question body: {}'.format(self.question_body)

    def prepare_to_update(self):
        self.answer_choices.clear()

    def calculate_score_for_s(self):
        score = Decimal(0)
        if self.max_score:
            for answer_choice_id in self.answer_choices:
                answer_choice = QuestionnaireQuestionChoice.objects.get(pk=answer_choice_id)
                score += (answer_choice.score / self.max_score) * 100

        return score

    def calculate_score_for_m(self):
        score = Decimal(0)
        if self.max_score:
            for answer_choice_id in self.answer_choices:
                answer_choice = QuestionnaireQuestionChoice.objects.get(pk=answer_choice_id)
                score += (answer_choice.score / self.max_score) * 100

        return score

    def calculate_score_for_t(self):
        return Decimal(0)

    def calculate_score_for_d(self):
        return Decimal(0)

    def calculate_score(self):
        self.score = getattr(self, 'calculate_score_for_{}'.format(self.type))()
        self.save()
        return (self.score * self.weight) / 100

    def coded_cause(self):
        return self.coded_causes.first()


class QuestionChoiceAbstract(models.Model):
    """
    Abstract class for a question choice

    """
    # Attributes
    text = models.CharField(max_length=255, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        abstract = True


class QuestionnaireTemplateQuestionChoice(QuestionChoiceAbstract):
    """

    """
    # Relation
    template_question = models.ForeignKey(QuestionnaireTemplateQuestion)

    class Meta:
        default_related_name = "template_question_choices"

    def __str__(self):
        return "Question: {}. text: {}".format(self.template_question.question_body, self.text)


class QuestionnaireQuestionChoice(QuestionChoiceAbstract):
    """

    """
    # Relation
    question = models.ForeignKey(QuestionnaireQuestion)

    class Meta:
        default_related_name = "question_choices"

    def __str__(self):
        return "Question: {}. text: {}".format(self.question.question_body, self.text)


class CrossIndexTemplate(models.Model):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate)
    question_templates = models.ManyToManyField(QuestionnaireTemplateQuestion, through='CrossIndexQuestionTemplate')

    # Attributes
    title = models.CharField(max_length=40)

    class Meta:
        default_related_name = 'cross_index_templates'

    def __str__(self):
        return '{}, TQuestionnaire: {}'.format(self.title, self.questionnaire_template.title)


class CrossIndex(models.Model):
    """

    """
    # Relations
    cross_index_template = models.ForeignKey(CrossIndexTemplate)
    questionnaire = models.ForeignKey(Questionnaire)
    questions = models.ManyToManyField(QuestionnaireQuestion, through='CrossIndexQuestion')

    # Attributes
    title = models.CharField(max_length=40)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        default_related_name = 'cross_indexes'

    def __str__(self):
        return '{}, Questionnaire: {}'.format(self.title, self.questionnaire.title)


class CrossIndexQuestionTemplate(models.Model):
    cross_index_template = models.ForeignKey(CrossIndexTemplate, on_delete=models.CASCADE)
    question_template = models.ForeignKey(QuestionnaireTemplateQuestion, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        default_related_name = 'cross_index_question_templates'


class CrossIndexQuestion(models.Model):
    cross_index = models.ForeignKey(CrossIndex, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionnaireQuestion, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2)



