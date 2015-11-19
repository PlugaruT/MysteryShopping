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
    script = models.ForeignKey(QuestionnaireScript,
                               related_name='questionnaires')

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


class QuestionnaireBlockTemplate(QuestionnaireBlockAbstract):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(QuestionnaireTemplate, related_name='block_templates')
    parent_block = models.ForeignKey('self', blank=True)

    def __str__(self):
        # TODO: find best representation of object
        return 'Template Block title: %s' % (self.title)


class QuestionnaireBlock(QuestionnaireBlockAbstract):
    """

    """
    # Relations
    questionnaire = models.ForeignKey(Questionnaire, related_name='blocks')
    # TODO: nu apare redundanţă
    parent_block = models.ForeignKey('self', blank=True)

    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        # TODO: find best representation of object
        return 'Block title: %s' % (self.title)

class QuestionAbstract(models.Model):
    """
    Abstract class for QuestionTemplate and Question
    """
    # Attributes
    question = models.CharField(max_length=200)
    comment = models.TextField(blank=True)
    show_comment = models.BooleanField()
    type = models.TextField()
    max_score = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True
        ordering = ('question',)

class QuestionTemplate(QuestionAbstract):
    """

    """
    # Relations
    # TODO: find if you need to add _template for the following fields
    questionnaire = models.ForeignKey(QuestionnaireTemplate)
    block = models.ForeignKey(QuestionnaireBlockTemplate)

    class Meta:
        default_related_name = 'question_templates'

    def __str__(self):
        return 'Question template body: %s' % self.question


class Question(QuestionAbstract):
    """

    """
    questionnaire = models.ForeignKey(Questionnaire)
    block = models.ForeignKey(QuestionnaireBlock)

    class Meta:
        default_related_name = 'questions'

    def __str__(self):
        return 'Question body: %s' % self.question
