from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# --- FIXED: Imported ProductImage at the top level ---
from .models import Product, ProductImage, Wishlist
from .forms import ProductForm

# Import Order and Feedback models to get counts for the dashboard
from message.models import Feedback

# Helper to protect admin routes
def is_admin(user):
    return user.is_authenticated and user.is_staff

# --- SECURE ADMIN VIEWS ---
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_products = Product.objects.count()
    total_messages = Feedback.objects.count()
    
    context = {
        'total_products': total_products,
        'total_messages': total_messages,
    }
    return render(request, 'products/admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_product_manage_view(request):
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(Product, id=edit_id) if edit_id else None

    if request.method == 'POST':
        # 1. Handle specific gallery image deletion
        if 'delete_gallery_image_id' in request.POST:
            img_id = request.POST.get('delete_gallery_image_id')
            ProductImage.objects.filter(id=img_id).delete()
            messages.success(request, "Specific gallery image removed.")
            return redirect(f"{request.path}?edit={edit_id}")

        # 2. Handle full product deletion
        if 'delete_id' in request.POST:
            del_id = request.POST.get('delete_id')
            Product.objects.filter(id=del_id).delete()
            messages.warning(request, "Product deleted permanently.")
            return redirect('admin_product_manage')
            
        # 3. Handle Product Creation/Editing
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            product = form.save()
            
            # Delete old images if clear box is checked
            if form.cleaned_data.get('clear_images'):
                product.images.all().delete()
                
            # Create new gallery images
            for f in request.FILES.getlist('additional_images'):
                ProductImage.objects.create(product=product, image=f)

            msg = "Product updated successfully!" if instance else "New product added!"
            messages.success(request, msg)
            return redirect('admin_product_manage')
    else:
        form = ProductForm(instance=instance)

    products = Product.objects.all().order_by('-created_at')
    
    # --- NEW: Get default categories + any custom ones already typed in the DB ---
    existing_categories = set(Product.objects.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True))
    default_categories = set(Product.DEFAULT_CATEGORIES)
    all_categories = sorted(list(existing_categories.union(default_categories)))
    
    context = {
        'form': form,
        'products': products,
        'edit_id': edit_id,
        'instance': instance,
        'all_categories': all_categories, # Passed to the HTML datalist
    }
    return render(request, 'products/admin/product_manage.html', context)

def mobile_ar_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/mobile_ar.html', {'product': product})

# UPDATE THESE TWO VIEWS IN views.py

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    wishlist_product_ids = []
    if request.user.is_authenticated:
        # ADD list() HERE to force it to a python list
        wishlist_product_ids = list(request.user.wishlist.values_list('product_id', flat=True))

    return render(request, 'products/detail.html', {
        'product': product,
        'wishlist_product_ids': wishlist_product_ids,
    })


def product_list_view(request):
    products = Product.objects.filter(status='Available').order_by('-created_at')
    available_categories = products.exclude(category__isnull=True).exclude(category__exact='').order_by('category').values_list('category', flat=True).distinct()
    
    category_filter = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    if category_filter and category_filter != 'All':
        products = products.filter(category=category_filter)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Fetch wishlist items for the logged-in user
    wishlist_product_ids = []
    if request.user.is_authenticated:
        # ADD list() HERE to force it to a python list
        wishlist_product_ids = list(request.user.wishlist.values_list('product_id', flat=True))

    context = {
        'products': products,
        'available_categories': available_categories,
        'current_category': category_filter if category_filter else 'All',
        'search_query': search_query,
        'wishlist_product_ids': wishlist_product_ids, 
    }
    return render(request, 'products/products.html', context)

def home_view(request):
    available_products = Product.objects.filter(status='Available')
    available_categories = available_products.exclude(category__isnull=True).exclude(category__exact='').order_by('category').values_list('category', flat=True).distinct()
    latest_products = available_products.order_by('-created_at')

    context = {
        'available_categories': available_categories,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)


# --- NEW WISHLIST VIEWS ---

def toggle_wishlist(request, product_id):
    """AJAX view to add or remove a product from the wishlist."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'}, status=401)
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})

@login_required
def wishlist_view(request):
    """View to display the user's wishlisted products."""
    wishlist_items = request.user.wishlist.select_related('product').all()
    # We pass the products specifically so they can easily use existing template designs
    products = [item.product for item in wishlist_items]
    
    # We also need to pass the IDs so the heart icons render as "filled"
    wishlist_product_ids = [p.id for p in products]

    context = {
        'products': products,
        'wishlist_product_ids': wishlist_product_ids,
        'is_wishlist_page': True,
    }
    # You can reuse the products.html template or create a specific wishlist.html
    return render(request, 'products/wishlist.html', context)