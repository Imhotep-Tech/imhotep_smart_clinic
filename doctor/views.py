from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients
from accounts.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import doctor_required
from datetime import datetime, date, timedelta
from django.urls import reverse

@login_required
@doctor_required
def dashboard(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    number_of_patients = doctor_profile.doctor_patients.count()

    #to be implemented
    number_of_patients_records=7
    
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
    todays_appointments = {
        'total': 5,
        'completed': 2
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

    context = {
        "user_data": request.user,
        "today_date": datetime.now(),
        "number_of_patients": number_of_patients,
        "number_of_patients_records": number_of_patients_records,
        "todays_appointments": todays_appointments,
        "avg_patients_per_day": avg_patients_per_day,
        "appointments_list": appointments_list
    }
    return render(request, "doctor_dashboard.html", context)

@login_required
@doctor_required
def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        doctor = get_object_or_404(DoctorProfile, user=request.user)

        new_patient = Patients.objects.create(
            name=name,
            phone_number=phone_number,
            gender=gender,
            date_of_birth=date_of_birth,
            doctor=doctor
        )
        try:
            new_patient.save()
            messages.success(request, "Patient Added successfully!")
            patient_id = new_patient.id
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
        except Exception as e:
            messages.error(request, f"Something went wrong while saving the new patient data: {str(e)}")
            return redirect("doctor_dashboard")
    context={
        "user_data": request.user
    }
    return render(request, "add_patient.html", context)

@login_required
@doctor_required
def show_patients(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patients = Patients.objects.filter(doctor=doctor_profile).order_by('name')
    context = {
        "user_data": request.user,
        "patients": patients
    }
    return render(request, "show_patients.html", context)

@login_required
@doctor_required
def show_patient_details(request):
    patient_id = request.GET.get('patient_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    # Update to get a single patient or 404 rather than a list
    patient = get_object_or_404(Patients, doctor=doctor_profile, id=patient_id)
    
    context = {
        "user_data": request.user,
        "patients": [patient] # Keep as list for compatibility with existing template
    }
    return render(request, "show_patient_details.html", context)

@login_required
@doctor_required
def update_patient(request):
    patient_id = request.GET.get('patient_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(Patients, doctor=doctor_profile, id=patient_id)

    if request.method == 'GET': 
        context = {
            "user_data": request.user,
            "patients": [patient]
        }
        return render(request, "edit_patient.html", context)

    name = request.POST.get('name')
    phone_number = request.POST.get('phone_number')
    gender = request.POST.get('gender')
    date_of_birth = request.POST.get('date_of_birth')

    patient.name = name
    patient.phone_number = phone_number
    patient.gender = gender
    patient.date_of_birth = date_of_birth

    try:
        patient.save()
        messages.success(request, "Patient Updated successfully!")
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)
    except Exception as e:
        messages.error(request, f"Something went wrong while saving the new patient data: {str(e)}")
        url = reverse('update_patient') + f'?patient_id={patient_id}'
        return redirect(url)

@login_required
@doctor_required
def delete_patient(request):
    patient_id = request.GET.get('patient_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    patient = get_object_or_404(Patients, doctor=doctor_profile, id=patient_id)

    if request.method == 'POST': 
        try:
            name = patient.name
            patient.delete()
            messages.success(request, f"Patient {name} Delete successfully!")
            return redirect("show_patients")
        except Exception as e:
            messages.error(request, f"Something went wrong while saving the new patient data: {str(e)}")
            url = reverse('update_patient') + f'?patient_id={patient_id}'
            return redirect(url)
    else:
        messages.error(request, "Method Not allowed")
        return redirect("doctor_dashboard")