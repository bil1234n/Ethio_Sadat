from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns =[
    path('', RedirectView.as_view(url='login/', permanent=False)),
    
    # Public B2B User Routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile_view, name='profile'), # ADD THIS LINE
    
    # Secure Admin Routes
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
]