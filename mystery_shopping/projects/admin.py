from django.contrib import admin

from .models import Project
from .models import ResearchMethodology
from .models import PlannedEvaluation
from .models import AccomplishedEvaluation


@admin.register(PlannedEvaluation, Project, ResearchMethodology, AccomplishedEvaluation)
class Projects(admin.ModelAdmin):
    pass
