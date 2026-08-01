import logging
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import User
from doctor.models import DoctorProfile, Patients, Clinic, Appointments

logger = logging.getLogger(__name__)

def get_landing_stats_data():
    try:
        doctor_user_count = User.objects.filter(user_type='doctor').count()
        doctor_profile_count = DoctorProfile.objects.count()
        doctors_count = max(doctor_user_count, doctor_profile_count)

        patient_user_count = User.objects.filter(user_type='patient').count()
        patient_record_count = Patients.objects.count()
        unlinked_patient_users = User.objects.filter(user_type='patient', patient_profile__isnull=True).count()
        patients_count = max(patient_user_count, patient_record_count + unlinked_patient_users)

        clinics_count = Clinic.objects.count()
        appointments_count = Appointments.objects.count()
    except Exception as e:
        logger.error(f"Error calculating landing stats: {e}", exc_info=True)
        doctors_count = 0
        patients_count = 0
        clinics_count = 0
        appointments_count = 0

    return {
        'patients_count': patients_count,
        'doctors_count': doctors_count,
        'clinics_count': clinics_count,
        'appointments_count': appointments_count,
    }

def landing_page(request):
    stats = get_landing_stats_data()
    return render(request, "landing_page.html", {'stats': stats})

def landing_stats_api(request):
    stats = get_landing_stats_data()
    return JsonResponse({
        'status': 'success',
        **stats
    })