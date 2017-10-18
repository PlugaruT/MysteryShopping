from django.contrib import admin

from mystery_shopping.respondents.models import Respondent


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    pass
