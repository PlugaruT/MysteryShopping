from django.contrib import admin

from .models import QuestionnaireScript
from .models import QuestionnaireTemplate
from .models import Questionnaire
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireBlock
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireQuestion
from .models import QuestionnaireTemplateQuestionChoice
from .models import QuestionnaireQuestionChoice


@admin.register(QuestionnaireScript, QuestionnaireTemplate, Questionnaire, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireTemplateQuestionChoice, QuestionnaireQuestionChoice)
class QuestionnaireAdmin(admin.ModelAdmin):
    pass

@admin.register(QuestionnaireQuestion)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_body', 'type', 'questionnaire', 'score', 'answer', 'answer_choices']