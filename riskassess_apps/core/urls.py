from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('resource/timeout/', views.resource_timeout, name='resource_timeout'),
    path('resource/hazards/', views.resource_hazard, name='resource_hazard'),
    path('resource/hierarchy/', views.resource_hierarchy, name='resource_hierarchy'),
    path('resource/controls/', views.resource_control, name='resource_control'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
]