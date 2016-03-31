from django.contrib import admin

from .models import CodedCauseLabel
from .models import CodedCause


@admin.register(CodedCauseLabel, CodedCause)
class CodedCause(admin.ModelAdmin):
    pass
