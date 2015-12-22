from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

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
    script = models.ForeignKey(QuestionnaireScript, null=True, blank=True,
                               related_name='template_questionnaires')
    description = models.TextField()

    def __str__(self):
        return 'Title: %s \n%s' % (self.title, self.script)


class Questionnaire(QuestionnaireAbstract):
    """
    The questionnaires that will contain answers.

    """
    # Relations
    script = models.ForeignKey(QuestionnaireScript, null=True, blank=True)
    template = models.ForeignKey(QuestionnaireTemplate)

    class Meta:
        default_related_name = 'questionnaires'

    def __str__(self):
        return 'Title: %s \n%s' % (self.title, self.script)


class QuestionnaireBlockAbstract(models.Model):
    """
    Abstract Questionnaire block for QuestionnaireBlockTemplate and QuestionnaireBlock

    """
    title = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=5, decimal_places=4)

    class Meta:
        abstract = True


class QuestionnaireTemplateBlock(QuestionnaireBlockAbstract, MPTTModel):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate, related_name='template_blocks')
    parent_block = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ('title',)
        parent_attr = 'parent_block'

    def __str__(self):
        return 'Title: %s' % self.title


class QuestionnaireBlock(QuestionnaireBlockAbstract, MPTTModel):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(Questionnaire, related_name='blocks')
    parent_block = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # Attributes
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class MPTTMeta:
        order_insertion_by = ('title',)
        parent_attr = 'parent_block'

    def __str__(self):
        return 'Title: %s' % self.title


class QuestionAbstract(models.Model):
    """
    Abstract class for QuestionTemplate and Question

    """
    # Attributes
    question_body = models.CharField(max_length=200)  # TODO: find optimal length
    type = models.TextField()
    show_comment = models.BooleanField()
    max_score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('question_body',)


class QuestionnaireTemplateQuestion(QuestionAbstract):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate, related_name='template_questions')
    template_block = models.ForeignKey(QuestionnaireTemplateBlock, related_name='template_block_questions')

    class Meta:
        default_related_name = 'question_templates'

    def __str__(self):
        return 'Question body: %s' % self.question_body


class QuestionnaireQuestion(QuestionAbstract):
    """

    """
    questionnaire = models.ForeignKey(Questionnaire)
    block = models.ForeignKey(QuestionnaireBlock)

    answer = models.TextField()
    comment = models.TextField(blank=True)

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return 'Question body: %s' % self.question_body
