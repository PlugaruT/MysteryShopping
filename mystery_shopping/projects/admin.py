from django.contrib import admin

from mystery_shopping.projects.models import Evaluation, EvaluationAssessmentComment, EvaluationAssessmentLevel, \
    Project, ResearchMethodology


@admin.register(Evaluation, ResearchMethodology, EvaluationAssessmentLevel, EvaluationAssessmentComment)
class Projects(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['company', 'period_start', 'period_end', 'type']
