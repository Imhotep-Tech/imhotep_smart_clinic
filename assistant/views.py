from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import assistant_required
from django.contrib import messages
from .models import AssistantProfile
from doctor.models import DoctorProfile

@login_required
@assistant_required
def dashboard(request):
    assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
    doctor_profile = assistant_profile.doctor
    
    context = {
        "user_data": request.user,
        "assistant_profile": assistant_profile,
        "doctor_profile": doctor_profile
    }
    
    return render(request, "assistant_dashboard.html", context)

@login_required
@assistant_required
def update_assistant_profile(request):
    assistant_profile = get_object_or_404(AssistantProfile, user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        
        try:
            user.save()
            messages.success(request, 'Your personal information was successfully updated!')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        "user_data": request.user,
        "assistant_profile": assistant_profile
    }
    
    return render(request, "update_assistant_profile.html", context)
