from django.contrib import admin
from .models import TimeoutQuestionnaire, TimeoutQuestion, Timeout, TimeoutAnswer, TimeoutHazard

class TimeoutQuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','description', 'business', 'haz_control_lines', 'created_at')
    search_fields = ('name',)
    list_filter = ('business',)

class TimeoutQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'questionnaire', 'question_text', 'preferred_answer', 'created_at')
    search_fields = ('questionnaire', 'question_text',)

class TimeoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'business', 'questionnaire', 'warning', 'created_at')
    search_fields = ('user', 'business', 'questionnaire')
    list_filter = ('business', 'questionnaire')

class TimeoutAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeout', 'question', 'answer', 'created_at')
    search_fields = ('timeout', 'question', 'answer')
    list_filter = ('timeout',)


class TimeoutHazardAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeout', 'hazard', 'control')
    search_fields = ('timeout', 'hazard', 'control')
    list_filter = ('timeout',)


admin.site.register(TimeoutQuestionnaire, TimeoutQuestionnaireAdmin)
admin.site.register(TimeoutQuestion, TimeoutQuestionAdmin)
admin.site.register(Timeout, TimeoutAdmin)
admin.site.register(TimeoutAnswer, TimeoutAnswerAdmin)
admin.site.register(TimeoutHazard, TimeoutHazardAdmin)