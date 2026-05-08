from django.urls import path
from .views import ProductListView, api_root, RegisterAPIView # <-- Import it here
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns =[
    path('', api_root, name='api-root'), 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('products/', ProductListView.as_view(), name='api_product_list'),
    
    # Add this line for Native Registration
    path('register/', RegisterAPIView.as_view(), name='api_register'), 
]