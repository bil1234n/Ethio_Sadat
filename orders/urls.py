# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:product_id>/', views.checkout_view, name='checkout'),
    path('verify/<str:tx_ref>/', views.verify_payment_view, name='verify_payment'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('admin-manage/', views.manage_orders_view, name='manage_orders'),
]