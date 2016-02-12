from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation
from .models import PlaceToAssess
from .models import EvaluationAssessmentLevel
from .models import EvaluationAssessmentComment


@admin.register(PlannedEvaluation, Project, ResearchMethodology, AccomplishedEvaluation, PlaceToAssess, EvaluationAssessmentLevel, EvaluationAssessmentComment)
class Projects(admin.ModelAdmin):
    pass
