from django.contrib import admin

from mystery_shopping.respondents.models import Respondent


@admin.register(Respondent)
class DetractorRespondentAdmin(admin.ModelAdmin):
    pass
