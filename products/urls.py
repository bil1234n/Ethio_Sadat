from django.urls import path
from . import views

urlpatterns =[
    # Public Routes
    path('', views.product_list_view, name='products'),
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    
    # Wishlist Routes
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Admin Routes
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('manage/', views.admin_product_manage_view, name='admin_product_manage'),
]