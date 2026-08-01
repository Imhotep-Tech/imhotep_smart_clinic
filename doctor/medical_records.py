import uuid
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients, MedicalRecord
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import doctor_required
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
import os
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML, CSS

@doctor_required
@login_required
def add_medical_record(request):
    if request.method == 'POST':
        patient_id = request.POST.get("patient_id")
        doctor = DoctorProfile.get_or_create_for_user(request.user)
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
            messages.success(request, _(f"Patient Record for {patient.name} Added successfully!"))
            patient_id = patient.id
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
        except Exception as e:
            messages.error(request, _(f"Something went wrong while saving the new record for patient: {str(e)}"))
            return redirect("doctor_dashboard")
    else:
        patient_id = request.GET.get('patient_id')
        doctor = DoctorProfile.get_or_create_for_user(request.user)
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
    doctor_profile = DoctorProfile.get_or_create_for_user(request.user)
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
        messages.success(request, _("Medical record updated successfully!"))
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)
    except Exception as e:
        messages.error(request, _(f"Something went wrong while updating the medical record: {str(e)}"))
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)

@login_required
@doctor_required
def delete_medical_record(request):
    medical_record_id = request.GET.get('medical_record_id')
    doctor_profile = DoctorProfile.get_or_create_for_user(request.user)
    medical_record = get_object_or_404(MedicalRecord, id=medical_record_id, doctor=doctor_profile)
    patient_id = medical_record.patient.id

    if request.method == 'POST': 
        try:
            name = medical_record.patient.name
            date = medical_record.date
            medical_record.delete()
            messages.success(request, _(f"Record deleted for {name} with date {date} successfully!"))
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
        except Exception as e:
            messages.error(request, _(f"Something went wrong while deleting the medical record: {str(e)}"))
            url = reverse('show_patient_details') + f'?patient_id={patient_id}'
            return redirect(url)
    else:
        messages.error(request, _("Method Not allowed"))
        return redirect("doctor_dashboard")

def _render_prescription_pdf_response(request, medical_record, inline=False):
    patient = medical_record.patient
    doctor_profile = medical_record.doctor
    
    formatted_date = str(medical_record.date).split(' ')[0]
    
    def has_arabic(text):
        if not text:
            return False
        return any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text)
    
    has_arabic_prescription = False
    if medical_record.prescription:
        has_arabic_prescription = has_arabic(medical_record.prescription)
    
    has_arabic_name = has_arabic(patient.name)
    doctor_user = doctor_profile.user
    doctor_name = f"{doctor_user.first_name} {doctor_user.last_name}".strip() or doctor_user.username
    has_arabic_doctor_name = has_arabic(doctor_name)
    has_arabic_specialization = has_arabic(doctor_profile.specialization)
    
    clinic_logo_path = None
    if doctor_profile.logo_path:
        clinic_logo_path = request.build_absolute_uri(settings.MEDIA_URL + doctor_profile.logo_path)
    
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
    
    html_string = render_to_string('prescription_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    filename = f"prescription_{patient.name}_{formatted_date}.pdf"
    disposition = 'inline' if inline else 'attachment'
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    html.write_pdf(response)
    return response

@login_required
@doctor_required
def generate_prescription_pdf(request, record_id):
    doctor_profile = DoctorProfile.get_or_create_for_user(request.user)
    medical_record = get_object_or_404(MedicalRecord, id=record_id, doctor=doctor_profile)
    return _render_prescription_pdf_response(request, medical_record, inline=False)

def shared_prescription_pdf(request, token):
    medical_record = get_object_or_404(MedicalRecord, share_token=token)
    if not medical_record.is_share_link_active():
        context = {
            'medical_record': medical_record,
            'error_message': _("This prescription share link is no longer shared or has expired."),
            'redirect_seconds': 10,
        }
        return render(request, 'shared_prescription_expired.html', context, status=403)
    
    return _render_prescription_pdf_response(request, medical_record, inline=True)

@login_required
@doctor_required
def toggle_prescription_share(request, record_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': str(_('Method Not allowed'))}, status=405)
    
    doctor_profile = DoctorProfile.get_or_create_for_user(request.user)
    medical_record = get_object_or_404(MedicalRecord, id=record_id, doctor=doctor_profile)
    
    action = request.POST.get('action', 'enable')
    expires_at_str = request.POST.get('expires_at', '')
    never_expires = request.POST.get('never_expires', 'false').lower() in ['true', '1', 'yes']
    
    if action == 'disable':
        medical_record.is_shareable = False
        medical_record.share_expires_at = None
        medical_record.save(update_fields=['is_shareable', 'share_expires_at'])
        return JsonResponse({
            'status': 'success',
            'is_shareable': False,
            'message': str(_('Prescription share link disabled successfully.')),
            'share_url': medical_record.get_share_url(request),
            'share_expires_at': None,
            'share_expires_at_formatted': None,
        })
    
    if not medical_record.share_token:
        medical_record.share_token = uuid.uuid4()
    
    medical_record.is_shareable = True
    
    if never_expires or not expires_at_str or expires_at_str.lower() in ['never', 'forever']:
        medical_record.share_expires_at = None
    else:
        try:
            parsed_dt = parse_datetime(expires_at_str)
            if parsed_dt is None:
                parsed_dt = datetime.fromisoformat(expires_at_str)
            if timezone.is_naive(parsed_dt):
                parsed_dt = timezone.make_aware(parsed_dt, timezone.get_current_timezone())
            medical_record.share_expires_at = parsed_dt
        except Exception:
            return JsonResponse({'status': 'error', 'message': str(_('Invalid expiration date format.'))}, status=400)
    
    medical_record.save()
    
    expires_formatted = medical_record.share_expires_at.strftime('%Y-%m-%d %H:%M') if medical_record.share_expires_at else str(_('Forever (No Expiration)'))
    
    return JsonResponse({
        'status': 'success',
        'is_shareable': True,
        'message': str(_('Prescription share link updated successfully.')),
        'share_url': medical_record.get_share_url(request),
        'share_expires_at': medical_record.share_expires_at.isoformat() if medical_record.share_expires_at else None,
        'share_expires_at_formatted': expires_formatted,
    })