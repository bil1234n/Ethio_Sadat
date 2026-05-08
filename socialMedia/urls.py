from django.urls import path
from .views import social_media_feed

app_name = 'socialMedia'

urlpatterns = [
    path('', social_media_feed, name='index'),
]