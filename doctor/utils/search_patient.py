from doctor.models import Patients

def search_patient_by_name(doctor_profile, patient_name):
    query = Patients.objects.filter(name__icontains=patient_name).order_by('name')
    if doctor_profile:
        if doctor_profile.clinic:
            query = query.filter(clinic=doctor_profile.clinic)
        else:
            query = query.filter(doctor=doctor_profile)
    return query

def search_patient_by_phone(doctor_profile, patient_phone):
    query = Patients.objects.filter(phone_number__icontains=patient_phone).order_by('name')
    if doctor_profile:
        if doctor_profile.clinic:
            query = query.filter(clinic=doctor_profile.clinic)
        else:
            query = query.filter(doctor=doctor_profile)
    return query