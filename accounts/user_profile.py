from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages

from django.contrib.auth import authenticate, login, get_backends
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

# Password reset views
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'
    form_class = PasswordChangeForm

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_done.html'

@login_required
def update_profile(request):
    
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        user_username = request.POST.get("username")
        user_email = request.POST.get("email")

        if first_name != user.first_name:
            user.first_name = first_name
            messages.info(request, "First name updated")
        if last_name != user.last_name:
            user.last_name = last_name
            messages.info(request, "Last name updated")

        user.save()
        
        if user.email == user_email and user.username == user_username:
            messages.info(request, "Nothing in the credentials has been updated!")
            if user.is_doctor():
                return redirect('update_doctor_profile')
            elif user.is_assistant():
                return redirect('update_assistant_profile')
            else:
                return redirect('login')
        
        # Check if username contains '@'
        if '@' in user_username:
            messages.error(request, "Username can't include @")
            if user.is_doctor():
                return redirect('update_doctor_profile')
            elif user.is_assistant():
                return redirect('update_assistant_profile')
            else:
                return redirect('login')
        
        # Check if email contains '@'
        if not '@' in user_email:
            messages.error(request, "Email must include @!")
            if user.is_doctor():
                return redirect('update_doctor_profile')
            elif user.is_assistant():
                return redirect('update_assistant_profile')
            else:
                return redirect('login')

        if user_username and user.username != user_username:

            # Check if username already exists
            if User.objects.filter(username=user_username).exists():
                messages.error(request, 'Username already taken, please choose another one!')
                if user.is_doctor():
                    return redirect('update_doctor_profile')
                elif user.is_assistant():
                    return redirect('update_assistant_profile')
                else:
                    return redirect('login')
            
            user.username = user_username
        
        if user_email and user_email != user.email:
            # Check if email already exists
            if User.objects.filter(email=user_email).exists():
                messages.error(request, 'Email already taken, please choose another one!')
                if user.is_doctor():
                    return redirect('update_doctor_profile')
                elif user.is_assistant():
                    return redirect('update_assistant_profile')
                else:
                    return redirect('login')
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Verify your new email address'
            
            # Fix: Create the verification URL correctly without 'accounts/' prefix
            # since it's already handled in the main URLconf
            verify_url = reverse('activate_profile_update', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'new_email': urlsafe_base64_encode(force_bytes(user_email))
            })
            
            message = render_to_string('activate_mail_change_send.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'verify_url': verify_url,
                'new_email': user_email
            })
            
            send_mail(mail_subject, '', 'no-reply@imhotep.com', [user_email], html_message=message)
            messages.success(request, "Email submitted successfully! Please check your email to verify your Email.")
            
            if user.is_doctor():
                return redirect('update_doctor_profile')
            elif user.is_assistant():
                return redirect('update_assistant_profile')
            else:
                return redirect('login')
                
        user.save()
        messages.success(request, 'Your profile was successfully updated!')
        
        if user.is_doctor():
            return redirect('update_doctor_profile')
        elif user.is_assistant():
            return redirect('update_assistant_profile')
        else:
            return redirect('login')

#the activate route
def activate_profile_update(request, uidb64, token, new_email):
    try:
        # Decode the user ID and new email
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        new_email = force_str(urlsafe_base64_decode(new_email))
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Update the user's email
        user.email = new_email
        user.is_active = True
        user.email_verify = True
        user.save()
        
        # Set the backend attribute on the user
        backend = get_backends()[0]
        user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
        
        # Log the user in
        login(request, user)
        messages.success(request, "Thank you for your email confirmation. Your email has been updated successfully.")
        
        if user.is_doctor():
            return redirect('doctor_dashboard')
        elif user.is_assistant():
            return redirect('assistant_dashboard')
        else:
            return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('login')