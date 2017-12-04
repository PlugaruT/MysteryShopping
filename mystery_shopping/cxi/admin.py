from django.contrib import admin

from mystery_shopping.cxi.models import CodedCause, CodedCauseLabel, ProjectComment, WhyCause


@admin.register(CodedCauseLabel, ProjectComment)
class CodedCauseLabelAdmin(admin.ModelAdmin):
    pass


@admin.register(CodedCause)
class CodedCause(admin.ModelAdmin):
    list_filter = ('project', 'sentiment')
    list_display = ('get_name', 'sentiment', 'get_number_of_why_causes', 'project')

    def get_name(self, obj):
        return obj.coded_label.name

    def get_number_of_why_causes(self, obj):
        return obj.raw_causes.count()


@admin.register(WhyCause)
class WhyCauseAdmin(admin.ModelAdmin):
    list_filter = ('is_appreciation_cause',)
    list_display = ('answer', 'is_appreciation_cause')
