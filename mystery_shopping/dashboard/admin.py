from django.contrib import admin

from .models import DashboardTemplate
from .models import DashboardComment


@admin.register(DashboardTemplate, DashboardComment)
class CodedCause(admin.ModelAdmin):
    pass
