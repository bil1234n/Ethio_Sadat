# orders/views.py
import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from .models import Order
from products.models import Product

# Helper for Admin access
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
def checkout_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if product.stock < quantity:
            messages.error(request, "Not enough stock available.")
            return redirect('product_detail_view', pk=product.id) # change route name if different in products/urls.py

        total_price = product.price * quantity
        tx_ref = f"B2B-{uuid.uuid4().hex[:12].upper()}" # Unique ref

        # Create Pending Order
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=total_price,
            tx_ref=tx_ref
        )

        # Chapa API Setup
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        return_url = request.build_absolute_uri(reverse('verify_payment', args=[tx_ref]))
        
        payload = {
            "amount": str(total_price),
            "currency": "ETB",
            "email": request.user.email or "customer@enterprise.com",
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "User",
            "tx_ref": tx_ref,
            "return_url": return_url,
            "customization[title]": "B2B Enterprise Hub",
            "customization[description]": f"Payment for {product.name}"
        }
        
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(chapa_url, json=payload, headers=headers)
        data = response.json()

        if data.get('status') == 'success':
            return redirect(data['data']['checkout_url'])
        else:
            messages.error(request, "Payment gateway error. Please try again.")
            return redirect('product_detail_view', pk=product.id)
            
    return redirect('home')

@login_required
def verify_payment_view(request, tx_ref):
    order = get_object_or_404(Order, tx_ref=tx_ref, user=request.user)
    
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        if order.status == 'Pending':
            order.status = 'Paid'
            order.product.stock -= order.quantity # Reduce Stock
            order.product.save()
            order.save()
            messages.success(request, "Payment successful! Your order has been placed.")
    else:
        order.status = 'Cancelled'
        order.save()
        messages.error(request, "Payment was not completed.")

    return redirect('my_orders')

@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@user_passes_test(is_admin)
def manage_orders_view(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} updated to {new_status}")
        return redirect('manage_orders')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/admin/manage_order.html', {'orders': orders})