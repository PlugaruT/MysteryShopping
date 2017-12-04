from django.contrib import admin

from mystery_shopping.questionnaires.models import CrossIndex, CrossIndexQuestion, CrossIndexQuestionTemplate, \
    CrossIndexTemplate, CustomWeight, Questionnaire, QuestionnaireBlock, QuestionnaireQuestion, \
    QuestionnaireQuestionChoice, QuestionnaireScript, QuestionnaireTemplate, QuestionnaireTemplateBlock, \
    QuestionnaireTemplateQuestion, QuestionnaireTemplateQuestionChoice, QuestionnaireTemplateStatus


@admin.register(QuestionnaireScript, QuestionnaireTemplateBlock, QuestionnaireBlock, QuestionnaireTemplateQuestion, QuestionnaireTemplateQuestionChoice, QuestionnaireQuestionChoice, CrossIndexTemplate, CrossIndex, CrossIndexQuestionTemplate, CrossIndexQuestion, QuestionnaireTemplateStatus, CustomWeight)
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
