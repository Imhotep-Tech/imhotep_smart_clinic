from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_required
from django.contrib import messages
from .models import DoctorProfile, AppointmentTimes
import os
from PIL import Image
from django.conf import settings
import uuid
import io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta

@login_required
@doctor_required
def update_doctor_profile(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        # Add any other doctor-specific fields here
        
        if specialization:
            doctor_profile.specialization = specialization
            
        try:
            doctor_profile.save()
            messages.success(request, 'Your professional details were successfully updated!')
            return redirect('update_doctor_profile')
        except Exception as e:
            messages.error(request, f'Error updating doctor profile: {str(e)}')
    
    # Get all appointment times and paginate
    appointment_times_list = AppointmentTimes.objects.filter(doctor=doctor_profile).order_by('day_of_the_week', 'start_time')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(appointment_times_list, 10)  # Show 10 items per page
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "user_data": request.user,
        "doctor_profile": doctor_profile,
        "page_obj": page_obj,
    }
    return render(request, "update_doctor_profile.html", context)

@login_required
@doctor_required
def upload_clinic_logo(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.user.is_demo:
        messages.error(request, "Demo accounts cannot update profile details. Please create your own account to access all features.")
        return redirect('update_doctor_profile')

    if request.method == 'POST' and request.FILES.get('clinic_logo'):
        uploaded_file = request.FILES['clinic_logo']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png']
        if uploaded_file.content_type not in allowed_types:
            messages.error(request, 'Only JPEG, or PNG images are allowed')
            return redirect('update_doctor_profile')
        
        # Validate file size (max 500KB)
        if uploaded_file.size > 500 * 1024:  # 500KB
            messages.error(request, 'Image size should not exceed 500KB')
            return redirect('update_doctor_profile')
        
        try:
            # Generate a unique filename
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            unique_filename = f"clinic_logo_{uuid.uuid4().hex[:10]}{ext}"
            
            # Create directory path
            upload_dir = os.path.join('clinic_logos', str(request.user.id))
            full_path = os.path.join(upload_dir, unique_filename)
            
            # Open and optimize image
            img = Image.open(uploaded_file)
            
            # Resize image to max dimensions of 300x300 while preserving aspect ratio
            img.thumbnail((300, 300))
            
            # Convert to RGB if image is RGBA (for PNG transparency)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Save optimized image to memory buffer
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', optimize=True, quality=85)
            buffer.seek(0)
            
            # Save to storage
            saved_path = default_storage.save(full_path, ContentFile(buffer.read()))
            
            # Update database
            doctor_profile.clinic_photo_path = saved_path
            doctor_profile.save()
            
            messages.success(request, 'Clinic logo uploaded successfully!')
        except Exception as e:
            messages.error(request, f'Error uploading logo: {str(e)}')
    
    return redirect('update_doctor_profile')

@login_required
@doctor_required
def remove_clinic_logo(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.user.is_demo:
        messages.error(request, "Demo accounts cannot update profile details. Please create your own account to access all features.")
        return redirect('update_doctor_profile')

    # Check if there's a logo to remove
    if doctor_profile.clinic_photo_path:
        try:
            # Delete the file from storage
            if default_storage.exists(doctor_profile.clinic_photo_path):
                default_storage.delete(doctor_profile.clinic_photo_path)
            
            # Clear the path in the database
            doctor_profile.clinic_photo_path = ''
            doctor_profile.save()
            
            messages.success(request, 'Clinic logo removed successfully!')
        except Exception as e:
            messages.error(request, f'Error removing logo: {str(e)}')
    else:
        messages.info(request, 'No logo to remove.')
    
    return redirect('update_doctor_profile')

@login_required
@doctor_required
def set_appointment_times(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        separation_time_str = request.POST.get('separation_time')
        day_of_the_week = request.POST.get('day_of_the_week')
        
        if start_time and end_time and separation_time_str and day_of_the_week:
            # Convert string time to timedelta
            hours, minutes, seconds = map(int, separation_time_str.split(':'))
            separation_time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            
            new_appointment_time = AppointmentTimes.objects.create(
                doctor=doctor_profile,
                start_time=start_time,
                end_time=end_time,
                separation_time=separation_time_delta,
                day_of_the_week=day_of_the_week
            )
        
            try:
                new_appointment_time.save()
                messages.success(request, 'Your appointment time were successfully added!')
                return redirect('update_doctor_profile')
            except Exception as e:
                messages.error(request, f'Error updating doctor profile: {str(e)}')
                return redirect('update_doctor_profile')
    
    context = {
        "user_data": request.user
    }
    return render(request, "set_appointment_times.html", context)

@login_required
@doctor_required
def update_appointment_times(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        appointment_time = get_object_or_404(AppointmentTimes, id=appointment_id, doctor=doctor_profile)

        appointment_time.start_time = request.POST.get('start_time')
        appointment_time.end_time = request.POST.get('end_time')
        
        # Convert string time to timedelta
        separation_time_str = request.POST.get('separation_time')
        if separation_time_str:
            hours, minutes, seconds = map(int, separation_time_str.split(':'))
            appointment_time.separation_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        appointment_time.day_of_the_week = request.POST.get('day_of_the_week')
        
        try:
            appointment_time.save()
            messages.success(request, 'Your appointment time were successfully updated!')
            return redirect('update_doctor_profile')
        except Exception as e:
            messages.error(request, f'Error updating doctor profile: {str(e)}')
            return redirect('update_doctor_profile')
    
    appointment_id = request.GET.get('appointment_id')
    appointment_time = get_object_or_404(AppointmentTimes, id=appointment_id, doctor=doctor_profile)
    context = {
        "user_data": request.user,
        "appointment_time": appointment_time
    }
    return render(request, "update_appointment_times.html", context)

@login_required
@doctor_required
def deactivate_appointment_times(request):

    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    if request.method == 'POST':
        appointment_id = request.GET.get('appointment_id')
        appointment_time = get_object_or_404(AppointmentTimes, id=appointment_id, doctor=doctor_profile)

        appointment_time.activated_status = not (appointment_time.activated_status)
        
        try:
            appointment_time.save()
            messages.success(request, 'Your appointment time were successfully updated!')
            return redirect('update_doctor_profile')
        except Exception as e:
            messages.error(request, f'Error updating doctor profile: {str(e)}')
            return redirect('update_doctor_profile')

    return redirect('update_doctor_profile')