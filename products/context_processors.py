from .models import Product

def global_categories(request):
    # This runs on EVERY page load, injecting categories into all templates (like header.html)
    categories = Product.objects.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True).distinct()
    return {
        'available_categories': categories
    }