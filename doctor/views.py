from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, MedicalRecord, Appointments
from assistant.models import AssistantProfile
from accounts.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.decorators import doctor_required
from datetime import datetime, date, timedelta
from django.contrib import messages

@login_required
@doctor_required
def dashboard(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)

    number_of_patients = doctor_profile.doctor_patients.count()

    patients_records = MedicalRecord.objects.filter(doctor=doctor_profile).order_by('-date')
    
    # to get the daily average
    today = date.today()

    latest_record = patients_records.first()
    latest_update = latest_record.date if latest_record else None

    if latest_update and hasattr(latest_update, 'date'):
        latest_update = latest_update.date()

    if latest_update == today:
        latest_update = "today"
    elif latest_update == (today - timedelta(days=1)):
        latest_update = "yesterday"

    number_of_patients_records = patients_records.count()
    
    thirty_days_ago = today - timedelta(days=30)
    patients_last_30_days = doctor_profile.doctor_patients.filter(
        date_added__gte=thirty_days_ago
    ).count()

    if patients_last_30_days > 0:
        avg_patients_per_day = round(patients_last_30_days / 30, 1)
    else:
        avg_patients_per_day = 0

    todays_appointments_today = Appointments.objects.filter(doctor=doctor_profile, date=date.today()).count()

    completed = Appointments.objects.filter(doctor=doctor_profile, date=date.today(), status='completed').count()

    todays_appointments = {
        'total': todays_appointments_today,
        'completed': completed
    }

    # Get appointments and implement pagination
    appointments_list = Appointments.objects.filter(doctor=doctor_profile, date=date.today()).order_by('-date', 'start_time')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(appointments_list, 5)  # Show 5 appointments per page
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "user_data": request.user,
        "today_date": datetime.now(),
        "number_of_patients": number_of_patients,
        "number_of_patients_records": number_of_patients_records,
        "todays_appointments": todays_appointments,
        "avg_patients_per_day": avg_patients_per_day,
        "appointments": appointments_list,
        "page_obj": page_obj,
        "latest_update":latest_update
    }
    return render(request, "doctor_dashboard.html", context)

def add_assistant(request):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    if request.method!="POST":
        context = {
            "user_data": request.user,
            "today_date": datetime.now(),
        }
        return render(request, 'add_assistant.html', context)
    else:
        username = request.POST.get('username')
        email = f"{username}@{doctor_profile.user.username}.com"
        password = request.POST.get('password')
        user_type = "assistant"
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Check if username contains '@'
        if '@' in username:
            messages.error(request, "Username can't include @")
            return render(request, "add_assistant.html", {"user_data": request.user})

        # Check if email contains '@' (this should always be true with our format)
        if not '@' in email:
            messages.error(request, "Email generation failed. Please try a different username.")
            return render(request, "add_assistant.html", {"user_data": request.user})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken, please choose another one!')
            return render(request, "add_assistant.html", {"user_data": request.user})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already taken, please choose another username!')
            return render(request, "add_assistant.html", {"user_data": request.user})

        # Create a new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            email_verify=True,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        if not doctor_profile:
            messages.error(request, 'Doctor profile not found. Assistant creation failed.')
            user.delete()
            return redirect("add_assistant")
            
        assistant = AssistantProfile.objects.create(
            user=user,
            doctor=doctor_profile
        )
        
        assistant.save()

        messages.success(request, "Assistant account created successfully!")
        return redirect("doctor_dashboard")
