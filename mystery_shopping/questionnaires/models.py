from django.db import models


class QuestionnaireScript(models.Model):
    """

    """
    # Attributes
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return '\nQuestionnaire script title: %s,\n' \
               'short description: %s' % (self.title, self.description[0:50])


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
    script = models.ForeignKey(QuestionnaireScript,
                               related_name='template_questionnaires')

    def __str__(self):
        return 'Questionnaire template name: %s \n%s' % (self.title, self.script)


class Questionnaire(QuestionnaireAbstract):
    """
    The questionnaires that will contain answers.

    """
    # Relations
    script = models.ForeignKey(QuestionnaireScript)
    template = models.ForeignKey(QuestionnaireTemplate)

    class Meta:
        default_related_name = 'questionnaires'

    def __str__(self):
        return 'Questionnaire name: %s \n%s' % (self.title, self.script)


class QuestionnaireBlockAbstract(models.Model):
    """
    Abstract Questionnaire block for QuestionnaireBlockTemplate and QuestionnaireBlock

    """
    title = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=4, decimal_places=4)

    class Meta:
        abstract = True


class QuestionnaireTemplateBlock(QuestionnaireBlockAbstract):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(QuestionnaireTemplate, related_name='template_blocks')
    parent_block = models.ForeignKey('self',blank=True, null=True)

    def __str__(self):
        return 'Template Block title: %s' % self.title


class QuestionnaireBlock(QuestionnaireBlockAbstract):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(Questionnaire, related_name='blocks')
    parent_block = models.ForeignKey('self', blank=True, null=True)

    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return 'Block title: %s' % (self.title)


class QuestionAbstract(models.Model):
    """
    Abstract class for QuestionTemplate and Question

    """
    # Attributes
    question_body = models.CharField(max_length=200)  # TODO: find optimal length
    type = models.TextField()
    show_comment = models.BooleanField()
    max_score = models.PositiveSmallIntegerField(null=True)

    class Meta:
        abstract = True
        ordering = ('question',)


class QuestionnaireTemplateQuestion(QuestionAbstract):
    """

    """
    # Relations
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate, related_name='template_questions')
    template_block = models.ForeignKey(QuestionnaireTemplateBlock, related_name='template_block_questions')

    class Meta:
        default_related_name = 'question_templates'

    def __str__(self):
        return 'Question template body: %s' % self.question


class QuestionnaireQuestion(QuestionAbstract):
    """

    """
    questionnaire = models.ForeignKey(Questionnaire)
    block = models.ForeignKey(QuestionnaireBlock)

    comment = models.TextField(blank=True)

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return 'Question body: %s' % self.question
