from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import Evaluation
from .models import PlaceToAssess
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment


@admin.register(Evaluation, Project, ResearchMethodology, PlaceToAssess, EvaluationAssessmentLevel, EvaluationAssessmentComment)
class Projects(admin.ModelAdmin):
    pass
