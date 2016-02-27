from decimal import Decimal

from django.db import models
from model_utils import Choices

from mptt.models import MPTTModel, TreeForeignKey

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

    def __str__(self):
        return 'Title: {}'.format(self.title)


class Questionnaire(QuestionnaireAbstract):
    """
    The questionnaires that will contain answers.

    """
    # Relations
    template = models.ForeignKey(QuestionnaireTemplate)

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.PositiveSmallIntegerField(default=100)

    class Meta:
        default_related_name = 'questionnaires'

    def __str__(self):
        return 'Title: {}'.format(self.title)

    def calculate_score(self):
        self.score = 0
        blocks = self.blocks.filter(parent_block=None)

        for block in blocks:
            self.score += block.calculate_score()

        self.save()

        return self.score


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
    type_choices = Choices(('t', 'Text Field'),
                           ('d', 'Date Field'),
                           ('s', 'Single Choice'),
                           ('m', 'Multiple Choice'))
    type = models.CharField(max_length=1, choices=type_choices, default=type_choices.t)
    max_score = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)

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

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    show_comment = models.BooleanField(default=True)
    comment = models.TextField(null=True, blank=True)
    answer_choices = models.ManyToManyField("QuestionnaireQuestionChoice", blank=True)

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return 'Question body: {}'.format(self.question_body)

    def prepare_to_update(self):
        self.answer_choices.clear()

    def calculate_score_for_s(self):
        choices = self.answer_choices.all()
        score = Decimal(0)
        for choice in choices:
            # TODO: check the correctness of computation in case max_score = 0
            score += (choice.score / self.max_score) * 100 if self.max_score else 0

        return score

    def calculate_score_for_m(self):
        choices = self.answer_choices.all()
        score = Decimal(0)
        for choice in choices:
            score += choice.score

        return (score / self.max_score) * 100

    def calculate_score_for_t(self):
        return Decimal(0)

    def calculate_score_for_d(self):
        return Decimal(0)

    def calculate_score(self):
        # calculate_score_for_ = {'s': self.calculate_score_for_s,
        #                         'm': self.calculate_score_for_m,
        #                         't': self.calculate_score_for_t,
        #                         'd': self.calculate_score_for_d}

        self.score = getattr(self, 'calculate_score_for_{}'.format(self.type))()
        self.save()
        return (self.score * self.weight) / 100


class QuestionChoiceAbstract(models.Model):
    """
    Abstract class for a question choice

    """
    # Attributes
    text = models.CharField(max_length=255, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)

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

