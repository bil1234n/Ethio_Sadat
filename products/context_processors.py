from .models import Product

def global_categories(request):
    # Added .filter(status='Available') and .order_by('category') to fix duplicates
    categories = Product.objects.filter(status='Available') \
        .exclude(category__isnull=True) \
        .exclude(category__exact='') \
        .order_by('category') \
        .values_list('category', flat=True) \
        .distinct()
        
    return {
        'available_categories': categories
    }