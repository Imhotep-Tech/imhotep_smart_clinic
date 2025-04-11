from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-patient/', views.add_patient, name='add_patient'),
]
