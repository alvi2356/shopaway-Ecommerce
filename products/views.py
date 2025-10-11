from django.shortcuts import render, get_object_or_404
from .models import Product, HeroSlide, Category
from django.core.cache import cache
from django.db.models import Q

def home(request):
    q = request.GET.get('q','')
    products = Product.objects.filter(active=True)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q))
    # filter by flags from navbar buttons
    if request.GET.get('super'):
        products = products.filter(is_super_sale=True)
    if request.GET.get('flash'):
        products = products.filter(is_flash_sale=True)
    if request.GET.get('mega'):
        products = products.filter(is_mega_sale=True)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    latest_products = Product.objects.filter(active=True, is_latest=True)[:8]
    super_sale = Product.objects.filter(active=True, is_super_sale=True)[:8]
    flash_sale = Product.objects.filter(active=True, is_flash_sale=True)[:8]
    mega_sale = Product.objects.filter(active=True, is_mega_sale=True)[:8]
    slides = HeroSlide.objects.filter(is_active=True)
    categories = Category.objects.all()[:12]  # Limit to 12 categories for the grid
    context = {
        'products': products[:50],
        'latest_products': latest_products,
        'super_sale': super_sale,
        'flash_sale': flash_sale,
        'mega_sale': mega_sale,
        'slides': slides,
        'categories': categories,
        'q': q
    }
    return render(request, 'products/home.html', context)

def product_detail(request, slug):
    p = get_object_or_404(Product.objects.prefetch_related('images'), slug=slug, active=True)
    images = list(p.images.all())
    return render(request, 'products/detail.html', {
        'product': p,
        'images': images,
    })

def all_products(request):
    """Display all products with filtering and search"""
    q = request.GET.get('q', '')
    products = Product.objects.filter(active=True)
    
    # Search functionality
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q))
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filter by sale types
    if request.GET.get('super'):
        products = products.filter(is_super_sale=True)
    if request.GET.get('flash'):
        products = products.filter(is_flash_sale=True)
    if request.GET.get('mega'):
        products = products.filter(is_mega_sale=True)
    if request.GET.get('latest'):
        products = products.filter(is_latest=True)
    
    # Filter by stock availability
    stock_filter = request.GET.get('stock')
    if stock_filter == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_filter == 'out_of_stock':
        products = products.filter(stock=0)
    
    # Ordering
    order_by = request.GET.get('order_by', 'name')
    if order_by in ['name', 'price', 'created_at']:
        products = products.order_by(order_by)
    elif order_by == 'price_desc':
        products = products.order_by('-price')
    elif order_by == 'stock_desc':
        products = products.order_by('-stock')
    
    context = {
        'products': products,
        'q': q,
        'category_slug': category_slug,
        'order_by': order_by,
        'stock_filter': stock_filter,
    }
    return render(request, 'products/all_products.html', context)
