# accounts/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    
    # Public User Routing Elements
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Security Administrator Portal Routing Paths
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    
    # OAuth API Callback Interfaces
    path('auth/google/callback/', views.google_login_callback, name='google_callback'),
]