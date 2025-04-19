from django.urls import path
from . import views, medical_records, patients, doctor_settings, appointments

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
    path('update-doctor-profile/', doctor_settings.update_doctor_profile, name='update_doctor_profile'),
    path('upload-clinic-logo/', doctor_settings.upload_clinic_logo, name='upload_clinic_logo'),
    path('remove-clinic-logo/', doctor_settings.remove_clinic_logo, name='remove_clinic_logo'),
    
    # Appointment times management
    path('set-appointment-times/', doctor_settings.set_appointment_times, name='set_appointment_times'),
    path('update-appointment-times/', doctor_settings.update_appointment_times, name='update_appointment_times'),
    path('deactivate-appointment-times/', doctor_settings.deactivate_appointment_times, name='deactivate_appointment_times'),
    
    # Appointment management
    path('appointments/', appointments.appointment_list, name='appointment_list'),
    path('appointment-detail/', appointments.appointment_detail, name='appointment_detail'),
    path('schedule-appointment/', appointments.schedule_appointment, name='schedule_appointment'),
    path('get_available_times/', appointments.get_available_times, name='get_available_times'),
    path('mark-appointment-completed/', appointments.mark_appointment, name='mark_appointment'),
    path('update-appointment/', appointments.update_appointment_doctor, name='update_appointment_doctor'),
    path('delete-appointment/', appointments.delete_appointment_doctor, name='delete_appointment_doctor'),

    path('add-assistant/',  views.add_assistant, name='add_assistant'),
]
