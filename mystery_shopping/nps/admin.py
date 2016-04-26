from django.contrib import admin

from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment


@admin.register(CodedCauseLabel, CodedCause, ProjectComment)
class CodedCause(admin.ModelAdmin):
    pass
