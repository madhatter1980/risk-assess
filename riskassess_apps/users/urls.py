from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('invite_signup/', views.invite_signup, name='invite_signup'),
    path('resend_link/<int:user_id>/', views.resend_link, name='resend_link'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('invite_confirm/<uidb64>/<token>/', views.invite_password_reset_confirm, name='invite_password_reset_confirm'),
]