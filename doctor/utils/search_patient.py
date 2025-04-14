from doctor.models import Patients

def search_patient_by_name(doctor_profile, patient_name):
    patients = Patients.objects.filter(
        doctor=doctor_profile,
        name__icontains=patient_name
    ).order_by('name')
    return patients

def search_patient_by_phone(doctor_profile, patient_phone):
    patients = Patients.objects.filter(
        doctor=doctor_profile,
        phone_number__icontains=patient_phone
    ).order_by('name')
    return patients