from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='assistant_dashboard'),
    path('update-profile/', views.update_assistant_profile, name='update_assistant_profile'),
]
