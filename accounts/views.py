# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import AdminRegistrationForm

def register_view(request):
    # Prevent logged-in users from viewing register page
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('/') 

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # The UserProfile is automatically created here by the Signal in models.py
            login(request, user)
            messages.success(request, f"Welcome to the B2B Hub, {user.username}! Account created successfully.")
            return redirect('/') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    # Prevent logged-in users from viewing login page
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('/') 

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Check if there is a 'next' URL (e.g., they tried to access a protected page)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            # Smart Redirect: If they are an admin, send to dashboard. Else, home.
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST': # Highly secure: only allow POST requests for logout
        logout(request)
        messages.info(request, "You have been securely logged out.")
        return redirect('login')
    
    # If they visit the URL via GET, log them out anyway but handle gracefully
    logout(request)
    return redirect('login')

# --- ADMIN SPECIFIC VIEWS ---
def admin_register_view(request):
    # Prevent logged-in users from viewing page
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('/')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # Create user but don't save to database yet
            user = form.save(commit=False)
            
            # Upgrade user to Admin status!
            user.is_staff = True
            user.is_superuser = True 
            user.save()
            
            login(request, user)
            messages.success(request, f"Admin account authorized and created! Welcome {user.username}.")
            
            # => Redirect to CUSTOM Admin Dashboard
            return redirect('admin_dashboard') 
        else:
            messages.error(request, "Authorization failed. Check the errors below.")
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'accounts/admin/admin_register.html', {'form': form})


def admin_login_view(request):
    # Prevent logged-in users from viewing page
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('/')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if this user is actually an admin
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome to the Admin Portal, {user.username}.")
                
                # => Redirect to CUSTOM Admin Dashboard
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access Denied: You do not have Administrator privileges.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/admin/admin_login.html', {'form': form})