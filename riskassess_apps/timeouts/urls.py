from django.urls import path

from . import views
from . import export_views


urlpatterns = [
    path('questionnaires/', views.questionnaires_list, name='questionnaires_list'),
    path('questionnaire/create/', views.questionnaire_create, name='questionnaire_create'),
    path('questionnaire/<int:pk>/delete/', views.questionnaire_delete, name='delete_questionnaire'),
    path('questionnaire/<int:questionnaire_id>/', views.questionnaire_detail, name='questionnaire_detail'),
    path('api/questionnaire/<int:questionnaire_id>/form/', views.timeout_questionnaire_form, name='timeout_question_form'),
    path('api/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('timeout/select/', views.timeout_select, name='timeout_select'),
    path('timeout/form/<int:questionnaire_id>/', views.timeout_form, name='timeout_form'),
    path('userlist', views.user_timeout_list, name='user_timeout_list'),
    path('list', views.timeout_list, name='timeout_list'),
    path('timeout/detail/<int:timeout_id>', views.timeout_detail, name='timeout_detail'),
    path('timeouts/export/csv/', export_views.export_timeouts_csv, name='export_timeouts_csv'),
    path('timeouts/export/pdf/', export_views.export_timeouts_pdf, name='export_timeouts_pdf'),
    path('timeouts/export/xlsx/', export_views.export_timeouts_xlsx, name='export_timeouts_xlsx'),
]