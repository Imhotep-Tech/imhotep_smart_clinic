from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients, MedicalRecord
from django.contrib import messages
from accounts.decorators import doctor_required
from django.urls import reverse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm

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

    patient = get_object_or_404(Patients, doctor=doctor_profile, id=patient_id)
    
    records = MedicalRecord.objects.filter(doctor=doctor_profile, patient=patient_id)

    context = {
        "user_data": request.user,
        "patients": [patient],
        "records":records
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
