from django.contrib import admin

from .models import QuestionnaireScript
from .models import QuestionnaireTemplateStatus
from .models import QuestionnaireTemplate
from .models import Questionnaire
from .models import QuestionnaireTemplateBlock
from .models import QuestionnaireBlock
from .models import QuestionnaireTemplateQuestion
from .models import QuestionnaireQuestion
from .models import QuestionnaireTemplateQuestionChoice
from .models import QuestionnaireQuestionChoice
from .models import CrossIndexTemplate
from .models import CrossIndex
from .models import CrossIndexQuestionTemplate
from .models import CrossIndexQuestion


@admin.register(QuestionnaireScript, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireTemplateQuestionChoice, QuestionnaireQuestionChoice, CrossIndexTemplate, CrossIndex, CrossIndexQuestionTemplate, CrossIndexQuestion, QuestionnaireTemplateStatus)
class QuestionnaireAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionnaireQuestion)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_body', 'type', 'questionnaire', 'score', 'answer', 'answer_choices']


@admin.register(QuestionnaireTemplate)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'tenant', 'is_editable']


@admin.register(Questionnaire)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'score']
