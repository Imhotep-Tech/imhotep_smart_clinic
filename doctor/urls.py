from django.urls import path
from . import views, medical_records, patients

urlpatterns = [
    path('dashboard/', views.dashboard, name='doctor_dashboard'),
    path('add-patient/', patients.add_patient, name='add_patient'),
    path('show-patients/', patients.show_patients, name='show_patients'),
    path('show-patient-details/', patients.show_patient_details, name='show_patient_details'),
    path('update-patient/', patients.update_patient, name='update_patient'),
    path('delete-patient/', patients.delete_patient, name='delete_patient'),
    path('add-medical-record/', medical_records.add_medical_record, name='add_medical_record'),
    path('update-medical-record/', medical_records.update_medical_record, name='update_medical_record'),
    path('delete-medical-record/', medical_records.delete_medical_record, name='delete_medical_record'),
    path('generate-prescription-pdf/<int:record_id>/', medical_records.generate_prescription_pdf, name='generate_prescription_pdf'),
    path('search-patient/', patients.search_patient, name='search_patient'),
]
