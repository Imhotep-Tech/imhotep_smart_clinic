from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients, MedicalRecord
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import doctor_required
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

@doctor_required
@login_required
def add_medical_record(request):
    if request.method == 'POST':
        patient_id = request.POST.get("patient_id")
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        patient = get_object_or_404(Patients,  doctor=doctor, id=patient_id)

        date = request.POST.get("date")
        details = request.POST.get("details")
        remarks = request.POST.get("remarks")
        prescription = request.POST.get("prescription")

        new_record = MedicalRecord.objects.create(
            doctor=doctor,
            patient=patient,
            date=date,
            details=details,
            remarks=remarks,
            prescription=prescription
        )

        try:
            new_record.save()
            messages.success(request, f"Patient Record for {patient.name} Added successfully!")
            patient_id = patient.id
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
        except Exception as e:
            messages.error(request, f"Something went wrong while saving the new record for patient: {str(e)}")
            return redirect("doctor_dashboard")
    else:
        patient_id = request.GET.get('patient_id')
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        patient = get_object_or_404(Patients, doctor=doctor, id=patient_id)
        
        context = {
            "user_data": request.user,
            "patient_name": patient.name,
            "patient_id": patient_id,
            "today_date":timezone.now
        }
        return render(request, "add_medical_record.html", context)

@login_required
@doctor_required
def update_medical_record(request):
    medical_record_id = request.GET.get('medical_record_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    medical_record = get_object_or_404(MedicalRecord, id=medical_record_id, doctor=doctor_profile)
    patient_id = medical_record.patient.id

    if request.method == 'GET': 
        context = {
            "user_data": request.user,
            "medical_record": medical_record,
            "patient_name": medical_record.patient.name,
            "patient_id": patient_id
        }
        return render(request, "edit_medical_record.html", context)

    date = request.POST.get('date')
    details = request.POST.get('details')
    remarks = request.POST.get('remarks')
    prescription = request.POST.get('prescription')

    medical_record.date = date
    medical_record.details = details
    medical_record.remarks = remarks
    medical_record.prescription = prescription

    try:
        medical_record.save()
        messages.success(request, "Medical record updated successfully!")
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)
    except Exception as e:
        messages.error(request, f"Something went wrong while updating the medical record: {str(e)}")
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)

@login_required
@doctor_required
def delete_medical_record(request):
    medical_record_id = request.GET.get('medical_record_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    medical_record = get_object_or_404(MedicalRecord, id=medical_record_id, doctor=doctor_profile)
    patient_id = medical_record.patient.id

    if request.method == 'POST': 
        try:
            name = medical_record.patient.name
            date = medical_record.date
            medical_record.delete()
            messages.success(request, f"Record deleted for {name} with date {date} successfully!")
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
        except Exception as e:
            messages.error(request, f"Something went wrong while deleting the medical record: {str(e)}")
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
    else:
        messages.error(request, "Method Not allowed")
        return redirect("doctor_dashboard")

@login_required
@doctor_required
def generate_prescription_pdf(request, record_id):
    # Get the medical record
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    medical_record = get_object_or_404(MedicalRecord, id=record_id, doctor=doctor_profile)
    patient = medical_record.patient
    
    # Format date to show only YYYY-MM-DD
    formatted_date = str(medical_record.date).split(' ')[0]
    
    # Helper function to check for Arabic text
    def has_arabic(text):
        return any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text)
    
    # Check if prescription content has Arabic
    has_arabic_prescription = False
    if medical_record.prescription:
        has_arabic_prescription = has_arabic(medical_record.prescription)
    
    # Check if patient name or doctor name contains Arabic
    has_arabic_name = has_arabic(patient.name)
    doctor_name = f"{request.user.first_name} {request.user.last_name}"
    has_arabic_doctor_name = has_arabic(doctor_name)
    has_arabic_specialization = has_arabic(doctor_profile.specialization)
    
    # Prepare the clinic logo path with absolute URL if it exists
    clinic_logo_path = None
    if doctor_profile.clinic_photo_path:
        # Get the absolute URL for the clinic logo
        clinic_logo_path = request.build_absolute_uri(settings.MEDIA_URL + doctor_profile.clinic_photo_path)
    
    # Prepare context for the template
    context = {
        'patient': patient,
        'medical_record': medical_record,
        'doctor_profile': doctor_profile,
        'formatted_date': formatted_date,
        'doctor_name': doctor_name,
        'doctor_specialization': doctor_profile.specialization,
        'has_arabic_name': has_arabic_name,
        'has_arabic': has_arabic_prescription,
        'has_arabic_doctor_name': has_arabic_doctor_name,
        'has_arabic_specialization': has_arabic_specialization,
        'clinic_logo_path': clinic_logo_path,
    }
    
    # Render the HTML template
    html_string = render_to_string('prescription_pdf.html', context)
    
    # Create HTTP response with PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"prescription_{patient.name}_{formatted_date}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Generate PDF from HTML
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    
    # Generate PDF and attach to response
    html.write_pdf(response)
    
    return response