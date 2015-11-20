from django.contrib import admin

from .models import QuestionnaireScript, QuestionnaireTemplate, Questionnaire, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireQuestion


@admin.register(QuestionnaireScript, QuestionnaireTemplate, Questionnaire, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireQuestion)
class QuestionnaireAdmin(admin.ModelAdmin):
    pass
