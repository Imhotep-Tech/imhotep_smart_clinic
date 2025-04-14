from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('show-patients/', views.show_patients, name='show_patients'),
    path('show-patient-details/', views.show_patient_details, name='show_patient_details'),
    path('update-patient/', views.update_patient, name='update_patient'),
    path('delete-patient/', views.delete_patient, name='delete_patient'),
    path('add-medical-record/', views.add_medical_record, name='add_medical_record'),
    path('update-medical-record/', views.update_medical_record, name='update_medical_record'),
    path('delete-medical-record/', views.delete_medical_record, name='delete_medical_record'),
     path('generate-prescription-pdf/<int:record_id>/', views.generate_prescription_pdf, name='generate_prescription_pdf'),
]
