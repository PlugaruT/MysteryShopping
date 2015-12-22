from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation


@admin.register(PlannedEvaluation, Project, ResearchMethodology)
class Projects(admin.ModelAdmin):
    pass
