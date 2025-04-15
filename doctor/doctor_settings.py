from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_required
from django.contrib import messages
from .models import DoctorProfile
import os
from PIL import Image
from django.conf import settings
import uuid
import io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
    
    context = {
        "user_data": request.user,
        "doctor_profile": doctor_profile,
    }
    return render(request, "update_doctor_profile.html", context)

@login_required
@doctor_required
def upload_clinic_logo(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
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