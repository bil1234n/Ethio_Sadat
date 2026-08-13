# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from .forms import AdminRegistrationForm, UserUpdateForm, UserProfileUpdateForm, UserProfileRegistrationForm, CustomUserCreationForm
from .models import Notification
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from django.contrib.auth.models import User

import sys

def google_login_callback(request):
    """Handles the seamless One-Tap Google Login securely with clock skew tolerance"""
    if request.method == 'POST':
        credential = request.POST.get('credential')
        if not credential:
            messages.error(request, "No credentials provided from Google.")
            return redirect('login')

        try:
            # FIX: Added clock_skew_in_seconds parameter to tolerate server time sync differences
            # Setting this to 10 seconds accounts for your 7-second time lag cleanly.
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            
            if not email:
                messages.error(request, "Google login failed. No email address associated with this account.")
                return redirect('login')

            # accounts/views.py (Inside your google_login_callback view)

            # 1. Force a case-insensitive lookup so 'Bilal' matches 'bilal'
            user = User.objects.filter(email__iexact=email).first()
            created = False
            
            if not user:
                # 2. Before creating a new user, make sure the username is safe
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # 3. Save the email as lowercase to normalize your data
                user = User.objects.create(
                    username=username,
                    email=email.lower(), 
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_unusable_password()
                user.save()
                created = True

            # Log the user in explicitly specifying the auth backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            if created:
                messages.success(request, f"Welcome {first_name}! Your account was successfully created via Google.")
            else:
                messages.success(request, f"Welcome back, {first_name}!")
                
            return redirect('profile') 

        except ValueError as e:
            print(f"GOOGLE AUTHENTICATION VALIDATION ERROR: {e}", file=sys.stderr)
            messages.error(request, f"Google token verification failed: {str(e)}")
            return redirect('login')

    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('profile') 

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    # Context explicitly includes GOOGLE_CLIENT_ID to ensure synchronization
    return render(request, 'accounts/login.html', {
        'form': form,
        'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', '')
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile') 

    if request.method == 'POST':
        # Use your custom form that includes email validation here
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileRegistrationForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = user.profile
            profile.phone_number = profile_form.cleaned_data.get('phone_number')
            profile.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome, {user.username}! Account created successfully.")
            return redirect('profile') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', '') # Pass Client ID to template
    })
    
def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('login')


def admin_register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('profile')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True 
            user.save()
            
            login(request, user)
            messages.success(request, f"Admin account authorized! Welcome {user.username}.")
            return redirect('admin_dashboard') 
        else:
            messages.error(request, "Authorization failed. Check the errors below.")
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'accounts/admin/admin_register.html', {'form': form})


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome to the Admin Portal, {user.username}.")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access Denied: Administrator privileges required.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/admin/admin_login.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {'u_form': u_form, 'p_form': p_form})


@login_required
def read_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('profile')