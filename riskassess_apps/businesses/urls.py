from django.urls import path

from . import views


urlpatterns = [
    path('add_business/', views.add_business, name='add_business'),
    path('business_profile/', views.business_profile, name='business_profile'),
    path('update_business/<uuid:business_id>/', views.update_business, name='update_business'),
    path('users/', views.business_users, name='business_users'),
    path('api/business-users/', views.api_business_users, name='api_business_users'),
    path('api/business-user/toggle_admin/<int:user_id>/', views.business_user_toggle_admin, name='toggle_admin'),
    path('api/business-user/delete/<int:user_id>/', views.delete_business_user, name='delete_business_user'),
]