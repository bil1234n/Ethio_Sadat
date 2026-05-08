from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('contact/', views.submit_feedback, name='contact'),
    path('history/', views.my_feedback, name='my_feedback'),
    
    # Custom Admin URLs
    path('manage/', views.admin_feedback_list, name='admin_feedback_list'),
    path('manage/reply/<int:pk>/', views.admin_reply_feedback, name='admin_reply_feedback'),
]