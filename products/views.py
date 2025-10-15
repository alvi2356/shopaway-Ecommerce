from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, HeroSlide, Category
from django.core.cache import cache
from django.db.models import Q, F, Case, When, IntegerField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import connection
import re

def enhanced_search(products, query):
    """Enhanced search with fuzzy matching and relevance scoring"""
    if not query or not query.strip():
        return products
    
    query = query.strip().lower()
    
    # Split query into individual words
    query_words = re.findall(r'\b\w+\b', query)
    
    if not query_words:
        return products
    
    # Create Q objects for different search strategies
    search_conditions = Q()
    
    # 1. Exact matches (highest priority)
    exact_match = Q(name__iexact=query) | Q(sku__iexact=query)
    
    # 2. Starts with matches (high priority)
    starts_with = Q(name__istartswith=query) | Q(sku__istartswith=query)
    
    # 3. Contains matches (medium priority)
    contains_match = Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query)
    
    # 4. Word-based matches (lower priority)
    word_conditions = Q()
    for word in query_words:
        if len(word) > 2:  # Only search for words longer than 2 characters
            word_conditions |= Q(name__icontains=word) | Q(description__icontains=word)
    
    # 5. Category name matches
    category_match = Q(category__name__icontains=query)
    
    # Combine all conditions
    search_conditions = exact_match | starts_with | contains_match | word_conditions | category_match
    
    # Apply search filter
    filtered_products = products.filter(search_conditions)
    
    # Add relevance scoring
    filtered_products = filtered_products.annotate(
        relevance_score=Case(
            # Exact matches get highest score
            When(name__iexact=query, then=100),
            When(sku__iexact=query, then=95),
            
            # Starts with gets high score
            When(name__istartswith=query, then=80),
            When(sku__istartswith=query, then=75),
            
            # Contains gets medium score
            When(name__icontains=query, then=60),
            When(description__icontains=query, then=40),
            When(sku__icontains=query, then=50),
            
            # Category matches get lower score
            When(category__name__icontains=query, then=30),
            
            # Default score for other matches
            default=20
        )
    ).order_by('-relevance_score', 'name')
    
    return filtered_products

def home(request):
    q = request.GET.get('q','')
    products = Product.objects.filter(active=True)
    if q:
        products = enhanced_search(products, q)
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
    
    # Enhanced search functionality
    if q:
        products = enhanced_search(products, q)
    
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

def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if len(query) >= 2:  # Only provide suggestions for queries with 2+ characters
        # Get product name suggestions
        product_suggestions = Product.objects.filter(
            active=True,
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        
        # Get category suggestions
        category_suggestions = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions = list(product_suggestions) + list(category_suggestions)
        suggestions = list(set(suggestions))[:8]  # Remove duplicates and limit to 8
    
    return JsonResponse({'suggestions': suggestions})

def search_results(request):
    """Dedicated search results page with enhanced functionality"""
    q = request.GET.get('q', '').strip()
    products = Product.objects.filter(active=True)
    search_results_count = 0
    
    if q:
        products = enhanced_search(products, q)
        search_results_count = products.count()
        
        # Add search analytics (optional - for tracking popular searches)
        # You can implement search analytics here if needed
    
    # Get related categories for the search
    related_categories = []
    if q:
        related_categories = Category.objects.filter(
            name__icontains=q
        )[:5]
    
    # Get popular products if no search results
    popular_products = []
    if not q or search_results_count == 0:
        popular_products = Product.objects.filter(
            active=True,
            stock__gt=0
        ).order_by('-created_at')[:12]
    
    context = {
        'products': products[:50],  # Limit results for performance
        'q': q,
        'search_results_count': search_results_count,
        'related_categories': related_categories,
        'popular_products': popular_products,
        'has_search': bool(q),
    }
    
    return render(request, 'products/search_results.html', context)
