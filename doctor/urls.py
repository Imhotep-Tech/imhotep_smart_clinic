from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('show-patients/', views.show_patients, name='show_patients'),
    path('show-patient-details/', views.show_patient_details, name='show_patient_details'),
]
