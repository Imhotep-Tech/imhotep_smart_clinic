from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Patients, MedicalRecord, Appointments, AppointmentTimes
from django.contrib import messages
from accounts.decorators import doctor_required
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
import datetime

@doctor_required
@login_required
def appointment_list(request):
    """View for showing a list of appointments."""
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    # Get filter parameters
    date_filter = request.GET.get('date')
    status_filter = request.GET.get('status')
    
    # Base queryset
    appointments = Appointments.objects.filter(doctor=doctor).order_by('-date', 'start_time')
    
    # Apply filters if provided
    if date_filter:
        try:
            filter_date = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date=filter_date)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    context = {
        "user_data": request.user,
        "appointments": appointments,
    }
    
    return render(request, "appointment_list.html", context)

@doctor_required
@login_required
def appointment_detail(request):
    """View for showing appointment details."""
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointment_id = request.GET.get('appointment_id')
    
    if not appointment_id:
        messages.error(request, "No appointment specified.")
        return redirect('appointment_list')
    
    try:
        appointment = get_object_or_404(Appointments, id=appointment_id, doctor=doctor)
        patient_id = appointment.patient.id
        url = reverse('show_patient_details') + f'?patient_id={patient_id}'
        return redirect(url)
    except Exception as e:
        messages.error(request, f"Error retrieving appointment details: {str(e)}")
        return redirect('appointment_list')

@doctor_required
@login_required
def get_available_times(request):
    """AJAX endpoint to get available appointment times for a date."""
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'No date provided'}, status=400)
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_the_week = selected_date.strftime('%A')
        
        # Get the doctor's scheduled hours for this date
        appointment_times = AppointmentTimes.objects.filter(
            doctor=doctor,
            day_of_the_week=day_of_the_week,
            activated_status=True
        ).order_by('start_time')

        # Get already booked appointments for this date
        booked_times = Appointments.objects.filter(
            doctor=doctor,
            date=selected_date
        ).values_list('start_time', flat=True)
        
        available_times = []
        
        for time_slot in appointment_times:
            # Generate all possible time slots between start_time and end_time
            current_time = datetime.datetime.combine(datetime.date.today(), time_slot.start_time)
            end_time = datetime.datetime.combine(datetime.date.today(), time_slot.end_time)
            
            # Convert separation_time from DurationField to minutes
            separation_minutes = time_slot.separation_time.total_seconds() // 60
            
            # Loop through all possible time slots
            while current_time < end_time:
                time_str = current_time.time().strftime('%H:%M:%S')
                
                # Check if this time is already booked
                if time_str not in [t.strftime('%H:%M:%S') for t in booked_times]:
                    available_times.append({
                        'value': time_str,
                        'display': current_time.time().strftime('%I:%M %p')
                    })
                
                # Move to the next time slot based on separation_time
                current_time += datetime.timedelta(minutes=int(separation_minutes))
        
        return JsonResponse({'available_times': available_times})
    
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@doctor_required
@login_required
def schedule_appointment(request):
    """View for scheduling a new appointment."""
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.method == 'POST':
        patient_id = request.POST.get("patient")
        date = request.POST.get("date")
        time_slot = request.POST.get("time_slot")
        
        try:
            patient = get_object_or_404(Patients, id=patient_id, doctor=doctor)
            
            # Check if an appointment already exists at this time
            existing_appointment = Appointments.objects.filter(
                doctor=doctor,
                date=date,
                start_time=time_slot
            ).exists()
            
            if existing_appointment:
                messages.error(request, "There is already an appointment scheduled at this time.")
                return redirect("schedule_appointment")
            
            # Create new appointment
            appointment = Appointments.objects.create(
                doctor=doctor,
                patient=patient,
                date=date,
                start_time=time_slot,
                status="scheduled"
            )
            
            messages.success(request, f"Appointment for {patient.name} scheduled successfully!")
            return redirect("appointment_list")
            
        except Exception as e:
            messages.error(request, f"Error scheduling appointment: {str(e)}")
            return redirect("schedule_appointment")
    else:
        # GET request - show the form
        patients = Patients.objects.filter(doctor=doctor).order_by('name')
        min_date = timezone.now().date()
        
        context = {
            "user_data": request.user,
            "patients": patients,
            "min_date": min_date,
        }
        
        return render(request, "schedule_appointment.html", context)

@login_required
@doctor_required
def update_appointment_doctor(request):
    """View for updating an existing appointment."""
    # Get parameters and validate
    appointment_id = request.GET.get('appointment_id')
    if not appointment_id:
        messages.error(request, "No appointment specified.")
        return redirect('appointment_list')
    
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    try:
        # Ensure the appointment exists and belongs to this doctor
        appointment = get_object_or_404(Appointments, id=appointment_id, doctor=doctor_profile)
        patient_id = appointment.patient.id
        
        if request.method == 'GET':
            # Get the minimum date (today or appointment date if in the past)
            min_date = max(timezone.now().date(), appointment.date)
            
            context = {
                "user_data": request.user,
                "appointments": appointment,
                "patient_id": patient_id,
                "min_date": min_date,
            }
            return render(request, "update_appointment_doctor.html", context)
        
        elif request.method == 'POST':
            # Validate inputs
            date = request.POST.get("date")
            start_time = request.POST.get("details")
            
            if not date or not start_time:
                messages.error(request, "Date and time are required.")
                return redirect(f"{reverse('update_appointment_doctor')}?appointment_id={appointment_id}")
            
            try:
                # Parse date to validate format
                parsed_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                
                # Check if date is in the past
                if parsed_date < timezone.now().date():
                    messages.error(request, "Cannot schedule appointments in the past.")
                    return redirect(f"{reverse('update_appointment_doctor')}?appointment_id={appointment_id}")
                
                # Check if time slot is available (excluding this appointment)
                existing_appointment = Appointments.objects.filter(
                    doctor=doctor_profile,
                    date=date,
                    start_time=start_time
                ).exclude(id=appointment_id).exists()
                
                if existing_appointment:
                    messages.error(request, "There is another appointment already scheduled at this time.")
                    return redirect(f"{reverse('update_appointment_doctor')}?appointment_id={appointment_id}")
                
                # Update appointment
                appointment.date = date
                appointment.start_time = start_time
                appointment.save()
                
                messages.success(request, f"Appointment for {appointment.patient.name} updated successfully!")
                return redirect("appointment_list")
                
            except ValueError:
                messages.error(request, "Invalid date or time format.")
                return redirect(f"{reverse('update_appointment_doctor')}?appointment_id={appointment_id}")
        
        else:
            messages.error(request, "Method not allowed.")
            return redirect("appointment_list")
            
    except Exception as e:
        messages.error(request, f"Error updating appointment: {str(e)}")
        return redirect("appointment_list")

@login_required
@doctor_required
def delete_appointment_doctor(request):

    appointment_id = request.GET.get('appointment_id')
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointments, id=appointment_id, doctor=doctor_profile)

    if request.method == 'POST': 
        try:
            name = appointment.patient.name
            date = appointment.date
            appointment.delete()
            messages.success(request, f"Appointment deleted for {name} with date {date} successfully!")
            return redirect('appointment_list')
        except Exception as e:
            messages.error(request, f"Something went wrong while deleting the medical record: {str(e)}")
            return redirect('appointment_list')
    else:
        messages.error(request, "Method Not allowed")
        return redirect("doctor_dashboard")

@doctor_required
@login_required
def mark_appointment(request):
    """View to mark an appointment as completed."""
    if request.method != 'POST':
        messages.error(request, "Method not allowed")
        return redirect("appointment_list")
    
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointment_id = request.POST.get('appointment_id')
    
    try:
        appointment = get_object_or_404(Appointments, id=appointment_id, doctor=doctor)
        
        # Toggle between 'scheduled' and 'completed'
        if appointment.status == 'scheduled':
            appointment.status = 'completed'
        else:
            appointment.status = 'scheduled'
            
        appointment.save()
        messages.success(request, f"Appointment with {appointment.patient.name} marked as {appointment.status}.")

        return redirect("appointment_list")

    except Exception as e:
        messages.error(request, f"Error updating appointment status: {str(e)}")
        return redirect("appointment_list")