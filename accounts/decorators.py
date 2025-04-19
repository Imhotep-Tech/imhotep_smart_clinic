from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
            
        if not request.user.is_doctor():
            messages.error(request, "You don't have permission to access doctor resources.")

            if request.user.is_assistant():
                return redirect("assistant_dashboard")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def assistant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
            
        if not request.user.is_assistant():
            messages.error(request, "You don't have permission to access assistant resources.")
            if request.user.is_doctor():
                return redirect("doctor_dashboard")
            
            if request.user.is_patient():
                return redirect("patient.dashboard")
            
            return redirect("login")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def doctor_or_assistant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
            
        if not (request.user.is_doctor() or request.user.is_assistant()):
            messages.error(request, "You don't have permission to access this resource.")
            
            if request.user.is_patient():
                return redirect("patient.dashboard")
            
            return redirect("login")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view