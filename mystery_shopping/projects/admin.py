from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import PlaceToAssess
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment


@admin.register(Evaluation, ResearchMethodology, EvaluationAssessmentLevel, EvaluationAssessmentComment)
class Projects(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['company', 'period_start', 'period_end', 'type']


@admin.register(PlaceToAssess)
class PlaceToAssessAdmin(admin.ModelAdmin):
    list_display = ['place_type', 'place_id', 'place', 'research_methodology']
