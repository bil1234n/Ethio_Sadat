from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q

from .models import Product
from .forms import ProductForm
# Import Order and Feedback models to get counts for the dashboard
from orders.models import Order
from message.models import Feedback

# Helper to protect admin routes
def is_admin(user):
    return user.is_authenticated and user.is_staff

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})

# --- SECURE ADMIN VIEWS ---
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # Fetch actual counts from the database
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_messages = Feedback.objects.count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_messages': total_messages,
    }
    return render(request, 'products/admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_product_manage_view(request):
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(Product, id=edit_id) if edit_id else None

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            del_id = request.POST.get('delete_id')
            Product.objects.filter(id=del_id).delete()
            messages.warning(request, "Product deleted permanently.")
            return redirect('admin_product_manage')
            
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            msg = "Product updated successfully!" if instance else "New product added!"
            messages.success(request, msg)
            return redirect('admin_product_manage')
    else:
        form = ProductForm(instance=instance)

    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'products': products,
        'edit_id': edit_id,
    }
    return render(request, 'products/admin/product_manage.html', context)

def mobile_ar_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/mobile_ar.html', {'product': product})

# --- PUBLIC USER VIEWS ---
def product_list_view(request):
    # Base Query: ONLY SHOW AVAILABLE PRODUCTS
    products = Product.objects.filter(status='Available').order_by('-created_at')

    # Fetch available unique categories from AVAILABLE products only
    available_categories = products.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True).distinct()
    
    # Get requested filters from URL query parameters
    category_filter = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    # Filter by category if a valid one is selected
    if category_filter and category_filter != 'All':
        products = products.filter(category=category_filter)

    # Filter by keyword search (searches name & description)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'available_categories': available_categories,
        'current_category': category_filter if category_filter else 'All',
        'search_query': search_query,
    }
    return render(request, 'products/products.html', context)


def home_view(request):
    # Base Query: ONLY SHOW AVAILABLE PRODUCTS
    available_products = Product.objects.filter(status='Available')

    # Get unique available categories from AVAILABLE products only
    available_categories = available_products.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True).distinct()
    
    # Get all AVAILABLE products ordered by newest
    latest_products = available_products.order_by('-created_at')

    context = {
        'available_categories': available_categories,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)