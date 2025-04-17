from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, MedicalRecord, Appointments
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import doctor_required
from datetime import datetime, date, timedelta

@login_required
@doctor_required
def dashboard(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    number_of_patients = doctor_profile.doctor_patients.count()

    #to be implemented
    number_of_patients_records = MedicalRecord.objects.filter(doctor=doctor_profile).count()
    
    #to get the daily average
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    patients_last_30_days = doctor_profile.doctor_patients.filter(
        date_added__gte=thirty_days_ago
    ).count()

    if patients_last_30_days > 0:
        avg_patients_per_day = round(patients_last_30_days / 30, 1)
    else:
        avg_patients_per_day = 0

    #to be implemented
    todays_appointments_today = Appointments.objects.filter(doctor=doctor_profile, date=date.today()).count()

    completed = Appointments.objects.filter(doctor=doctor_profile, date=date.today(), status='completed').count()

    todays_appointments = {
        'total': todays_appointments_today,
        'completed': completed
    }

    #to be implemented
    appointments_list = [
        {
            'time': '9:00 AM',
            'patient_name': 'John Doe',
            'patient_initials': 'JD',
            'patient_gender': 'Male',
            'patient_age': 42,
            'status': 'Completed',
            'status_color': 'green'
        },
        {
            'time': '11:30 AM',
            'patient_name': 'Maria Smith',
            'patient_initials': 'MS',
            'patient_gender': 'Female',
            'patient_age': 35,
            'status': 'In Progress',
            'status_color': 'blue'
        },
        {
            'time': '2:00 PM',
            'patient_name': 'Robert Johnson',
            'patient_initials': 'RJ',
            'patient_gender': 'Male',
            'patient_age': 58,
            'status': 'Scheduled',
            'status_color': 'yellow'
        }
    ]
    
    appointments = Appointments.objects.filter(doctor=doctor_profile).order_by('-date', 'start_time')
    for i in appointments:
        print(i)
    context = {
        "user_data": request.user,
        "today_date": datetime.now(),
        "number_of_patients": number_of_patients,
        "number_of_patients_records": number_of_patients_records,
        "todays_appointments": todays_appointments,
        "avg_patients_per_day": avg_patients_per_day,
        "appointments": appointments
    }
    return render(request, "doctor_dashboard.html", context)
