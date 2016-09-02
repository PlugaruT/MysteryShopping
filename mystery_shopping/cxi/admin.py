from django.contrib import admin

from .models import CodedCauseLabel
from .models import CodedCause
from .models import ProjectComment
from .models import WhyCause


@admin.register(CodedCauseLabel, CodedCause, ProjectComment, WhyCause)
class CodedCause(admin.ModelAdmin):
    pass
