from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Product
from .forms import ProductForm

# Helper to protect admin routes
def is_admin(user):
    return user.is_authenticated and user.is_staff

# --- PUBLIC USER VIEWS ---
def product_list_view(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/products.html', {'products': products})

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})

# --- SECURE ADMIN VIEWS ---
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_products = Product.objects.count()
    # You can add total orders and revenue here later
    return render(request, 'products/admin/dashboard.html', {'total_products': total_products})

@user_passes_test(is_admin)
def admin_product_manage_view(request):
    # Determine if we are editing an existing product
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(Product, id=edit_id) if edit_id else None

    if request.method == 'POST':
        # Handle Delete Action
        if 'delete_id' in request.POST:
            del_id = request.POST.get('delete_id')
            Product.objects.filter(id=del_id).delete()
            messages.warning(request, "Product deleted permanently.")
            return redirect('admin_product_manage')
            
        # Handle Add / Edit Action
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            msg = "Product updated successfully!" if instance else "New product added!"
            messages.success(request, msg)
            return redirect('admin_product_manage')
    else:
        form = ProductForm(instance=instance)

    # Fetch all products for the table
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'products': products,
        'edit_id': edit_id, # Tells template if we are in "Edit Mode"
    }
    return render(request, 'products/admin/product_manage.html', context)