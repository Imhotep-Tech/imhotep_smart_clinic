from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients, MedicalRecord
from assistant.models import AssistantProfile
from django.contrib import messages
from accounts.decorators import doctor_required, doctor_or_assistant_required
from django.urls import reverse
from django.db.models import Q
from .utils.search_patient import search_patient_by_name, search_patient_by_phone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date

@login_required
@doctor_required  # Only doctors can add patients
def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name').title()
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        doctor = get_object_or_404(DoctorProfile, user=request.user)

        if date_of_birth:
            new_patient = Patients.objects.create(
                name=name,
                phone_number=phone_number,
                gender=gender,
                date_of_birth=date_of_birth,
                doctor=doctor
            )
        else:
            new_patient = Patients.objects.create(
                name=name,
                phone_number=phone_number,
                gender=gender,
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
@doctor_or_assistant_required  # Both doctors and assistants can view patient lists
def show_patients(request):
    # Get the appropriate doctor profile
    if request.user.is_doctor():
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    else:  # Assistant
        assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
        doctor_profile = assistant_profile.doctor
        
    patients_list = Patients.objects.filter(doctor=doctor_profile).order_by('name')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(patients_list, 10)  # Show 10 patients per page
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "user_data": request.user,
        "patients": patients_list,
        "page_obj": page_obj
    }
    return render(request, "show_patients.html", context)

@login_required
@doctor_or_assistant_required  # Both doctors and assistants can view patient details
def show_patient_details(request):
    patient_id = request.GET.get('patient_id')
    
    # Get the appropriate doctor profile
    if request.user.is_doctor():
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    else:  # Assistant
        assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
        doctor_profile = assistant_profile.doctor
    
    patient = get_object_or_404(Patients, doctor=doctor_profile, id=patient_id)
    records_list = MedicalRecord.objects.filter(doctor=doctor_profile, patient=patient_id).order_by('-date')

    if patient.date_of_birth:
        today = date.today()
        patient_birthdate = patient.date_of_birth

        patient_age = today.year - patient_birthdate.year - (
            (today.month, today.day) < (patient_birthdate.month, patient_birthdate.day)
        )
    else:
        patient_age = None

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(records_list, 10)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "user_data": request.user,
        "patients": [patient],
        "records": records_list,
        "page_obj": page_obj,
        "patient_age": patient_age
    }
    return render(request, "show_patient_details.html", context)

@login_required
@doctor_or_assistant_required  # Both doctors and assistants can update patient basic info
def update_patient(request):
    patient_id = request.GET.get('patient_id')
    
    # Get the appropriate doctor profile
    if request.user.is_doctor():
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    else:  # Assistant
        assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
        doctor_profile = assistant_profile.doctor
        
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
@doctor_required  # Only doctors can delete patients
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
    
@login_required
@doctor_or_assistant_required  # Both doctors and assistants can search patients
def search_patient(request):
    # Get the appropriate doctor profile
    if request.user.is_doctor():
        doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    else:  # Assistant
        assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
        doctor_profile = assistant_profile.doctor
    
    patient_name = request.GET.get('patient_name', '')
    patient_phone = request.GET.get('patient_phone', '')
    
    if patient_name:
        patients_list = search_patient_by_name(doctor_profile, patient_name)
    elif patient_phone:
        patients_list = search_patient_by_phone(doctor_profile, patient_phone)
    else:
        patients_list = []
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(patients_list, 10)  # Show 10 patients per page
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "user_data": request.user,
        "patients": patients_list,
        "page_obj": page_obj
    }
    return render(request, "show_patients.html", context)
