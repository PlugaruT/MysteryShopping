from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation
from .models import PlaceToAssess


@admin.register(PlannedEvaluation, Project, ResearchMethodology, AccomplishedEvaluation, PlaceToAssess)
class Projects(admin.ModelAdmin):
    pass
