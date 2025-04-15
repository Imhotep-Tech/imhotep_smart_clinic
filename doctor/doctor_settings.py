from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_required
from django.contrib import messages
from .models import DoctorProfile

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