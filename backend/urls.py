# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views 
from accounts import views as accounts_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls'), name='products'),
    path('', product_views.home_view, name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    
    # CHANGED: Points to the dynamic app instead of TemplateView
    path('socialMedia/', include('socialMedia.urls')), 
    
    path('api/', include('api.urls')),
    
    path('message/', include('message.urls')), 
    path('notification/read/<int:notif_id>/', accounts_views.read_notification, name='read_notification'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)