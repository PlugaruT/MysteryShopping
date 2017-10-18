from django.contrib import admin

from mystery_shopping.respondents.models import Respondent, RespondentCase


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_filter = ('number_of_questions',)
    list_display = ('view_place', 'number_of_questions')

    def view_place(self, obj):
        return obj.get_visited_place().element_name


@admin.register(RespondentCase)
class RespondentCaseAdmin(admin.ModelAdmin):
    list_filter = ('state', 'follow_up_date')
    list_display = ('view_place', 'state', 'created')

    def view_place(self, obj):
        return obj.respondent.get_visited_place().element_name
