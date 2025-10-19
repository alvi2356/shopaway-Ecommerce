from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
import json

from orders.models import Order, OrderItem
from products.models import Product, Category
from analytics.models import (
    AnalyticsEvent, SalesAnalytics, ProductAnalytics, 
    CustomerAnalytics, AnalyticsDashboard, AnalyticsWidget
)


@login_required
def dashboard(request):
    """Main analytics dashboard with real-time data"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Get or create today's sales analytics
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    
    # Calculate real-time metrics
    context = {
        # Today's metrics
        'total_sales_today': sales_today.total_sales,
        'orders_today': sales_today.total_orders,
        'products_sold_today': sales_today.total_products_sold,
        'avg_order_value_today': sales_today.average_order_value,
        'new_customers_today': sales_today.new_customers,
        
        # This month's metrics
        'total_sales_month': SalesAnalytics.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('total_sales'))['total'] or 0,
        'orders_month': SalesAnalytics.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('total_orders'))['total'] or 0,
        
        # This week's metrics
        'total_sales_week': SalesAnalytics.objects.filter(
            date__gte=week_start
        ).aggregate(total=Sum('total_sales'))['total'] or 0,
        'orders_week': SalesAnalytics.objects.filter(
            date__gte=week_start
        ).aggregate(total=Sum('total_orders'))['total'] or 0,
        
        # Payment method breakdown
        'cod_orders_today': sales_today.cod_orders,
        'online_orders_today': sales_today.online_orders,
        'cod_revenue_today': sales_today.cod_revenue,
        'online_revenue_today': sales_today.online_revenue,
        
        # Order status breakdown
        'pending_orders': sales_today.pending_orders,
        'confirmed_orders': sales_today.confirmed_orders,
        'shipped_orders': sales_today.shipped_orders,
        'delivered_orders': sales_today.delivered_orders,
        'cancelled_orders': sales_today.cancelled_orders,
        
        # Recent activity
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:10],
        'recent_events': AnalyticsEvent.objects.select_related('user').order_by('-created_at')[:10],
        
        # Top products
        'top_products': get_top_products(),
        'top_categories': get_top_categories(),
        
        # Chart data
        'sales_chart_data': get_sales_chart_data(),
        'orders_chart_data': get_orders_chart_data(),
        'payment_method_data': get_payment_method_data(),
        'order_status_data': get_order_status_data(),
    }
    
    return render(request, 'analytics/dashboard.html', context)


def get_top_products(limit=10):
    """Get top performing products by revenue"""
    return ProductAnalytics.objects.select_related('product').filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).values('product__name', 'product__id').annotate(
        total_revenue=Sum('revenue'),
        total_units=Sum('units_sold'),
        total_views=Sum('page_views')
    ).order_by('-total_revenue')[:limit]


def get_top_categories(limit=5):
    """Get top performing categories"""
    return OrderItem.objects.filter(
        order__created_at__gte=timezone.now().date() - timedelta(days=30)
    ).values('product__category__name').annotate(
        total_revenue=Sum(F('price') * F('qty')),
        total_orders=Count('order', distinct=True),
        total_products=Count('product', distinct=True)
    ).order_by('-total_revenue')[:limit]


def get_sales_chart_data(days=30):
    """Get sales data for chart visualization"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    sales_data = SalesAnalytics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    return {
        'labels': [str(item.date) for item in sales_data],
        'datasets': [{
            'label': 'Daily Sales',
            'data': [float(item.total_sales) for item in sales_data],
            'borderColor': 'rgb(75, 192, 192)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'tension': 0.1
        }]
    }


def get_orders_chart_data(days=30):
    """Get orders data for chart visualization"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    orders_data = SalesAnalytics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    return {
        'labels': [str(item.date) for item in orders_data],
        'datasets': [{
            'label': 'Daily Orders',
            'data': [item.total_orders for item in orders_data],
            'borderColor': 'rgb(255, 99, 132)',
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'tension': 0.1
        }]
    }


def get_payment_method_data():
    """Get payment method breakdown data"""
    today = timezone.now().date()
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    
    return {
        'labels': ['Cash on Delivery', 'Online Payment'],
        'datasets': [{
            'data': [float(sales_today.cod_revenue), float(sales_today.online_revenue)],
            'backgroundColor': ['#FF6384', '#36A2EB'],
            'borderWidth': 1
        }]
    }


def get_order_status_data():
    """Get order status breakdown data"""
    today = timezone.now().date()
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    
    return {
        'labels': ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'],
        'datasets': [{
            'data': [
                sales_today.pending_orders,
                sales_today.confirmed_orders,
                sales_today.shipped_orders,
                sales_today.delivered_orders,
                sales_today.cancelled_orders
            ],
            'backgroundColor': [
                '#FFC107', '#17A2B8', '#28A745', '#007BFF', '#DC3545'
            ],
            'borderWidth': 1
        }]
    }


@cache_page(60 * 5)  # Cache for 5 minutes
def analytics_api(request):
    """API endpoint for analytics data"""
    data_type = request.GET.get('type', 'overview')
    
    if data_type == 'overview':
        return JsonResponse(get_overview_data())
    elif data_type == 'sales':
        return JsonResponse(get_sales_chart_data())
    elif data_type == 'orders':
        return JsonResponse(get_orders_chart_data())
    elif data_type == 'products':
        return JsonResponse({'products': list(get_top_products())})
    elif data_type == 'products_overview':
        return JsonResponse(get_products_overview_data())
    elif data_type == 'categories':
        return JsonResponse({'categories': list(get_top_categories())})
    elif data_type == 'payment_methods':
        return JsonResponse(get_payment_method_data())
    elif data_type == 'order_status':
        return JsonResponse(get_order_status_data())
    
    return JsonResponse({'error': 'Invalid data type'}, status=400)


def get_overview_data():
    """Get overview analytics data"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Get today's data
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    
    # Calculate growth rates
    yesterday = today - timedelta(days=1)
    sales_yesterday = SalesAnalytics.get_or_create_for_date(yesterday)
    
    sales_growth = 0
    if sales_yesterday.total_sales > 0:
        sales_growth = ((sales_today.total_sales - sales_yesterday.total_sales) / sales_yesterday.total_sales) * 100
    
    orders_growth = 0
    if sales_yesterday.total_orders > 0:
        orders_growth = ((sales_today.total_orders - sales_yesterday.total_orders) / sales_yesterday.total_orders) * 100
    
    return {
        'today': {
            'sales': float(sales_today.total_sales),
            'orders': sales_today.total_orders,
            'products_sold': sales_today.total_products_sold,
            'avg_order_value': float(sales_today.average_order_value),
            'new_customers': sales_today.new_customers,
        },
        'growth': {
            'sales_growth': round(sales_growth, 2),
            'orders_growth': round(orders_growth, 2),
        },
        'month': {
            'sales': float(SalesAnalytics.objects.filter(
                date__gte=month_start
            ).aggregate(total=Sum('total_sales'))['total'] or 0),
            'orders': SalesAnalytics.objects.filter(
                date__gte=month_start
            ).aggregate(total=Sum('total_orders'))['total'] or 0,
        },
        'week': {
            'sales': float(SalesAnalytics.objects.filter(
                date__gte=week_start
            ).aggregate(total=Sum('total_sales'))['total'] or 0),
            'orders': SalesAnalytics.objects.filter(
                date__gte=week_start
            ).aggregate(total=Sum('total_orders'))['total'] or 0,
        }
    }


def get_products_overview_data():
    """Get products overview analytics data"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get top products for last 30 days
    top_products = ProductAnalytics.objects.select_related('product').filter(
        date__gte=today - timedelta(days=30)
    ).values('product__name', 'product__id').annotate(
        total_revenue=Sum('revenue'),
        total_units=Sum('units_sold'),
        total_views=Sum('page_views'),
        avg_conversion_rate=Avg('view_to_purchase_rate')
    ).order_by('-total_revenue')[:10]
    
    # Get category performance
    category_performance = ProductAnalytics.objects.select_related('product__category').filter(
        date__gte=today - timedelta(days=30)
    ).values('product__category__name').annotate(
        total_revenue=Sum('revenue'),
        total_units=Sum('units_sold'),
        total_views=Sum('page_views'),
        product_count=Count('product', distinct=True),
        avg_conversion_rate=Avg('view_to_purchase_rate')
    ).order_by('-total_revenue')
    
    return {
        'top_products': list(top_products),
        'category_performance': list(category_performance),
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(active=True).count(),
        'total_categories': Category.objects.count(),
    }


def track_event(request):
    """Track analytics events"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            event = AnalyticsEvent.objects.create(
                event_type=data.get('event_type'),
                user=request.user if request.user.is_authenticated else None,
                session_id=data.get('session_id'),
                page_url=data.get('page_url'),
                page_title=data.get('page_title'),
                referrer=data.get('referrer'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                ip_address=get_client_ip(request),
                product_id=data.get('product_id'),
                product_name=data.get('product_name'),
                product_category=data.get('product_category'),
                product_price=data.get('product_price'),
                quantity=data.get('quantity', 1),
                transaction_id=data.get('transaction_id'),
                transaction_value=data.get('transaction_value'),
                metadata=data.get('metadata', {})
            )
            
            return JsonResponse({'status': 'success', 'event_id': event.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def product_analytics(request, product_id):
    """Product-specific analytics"""
    product = get_object_or_404(Product, id=product_id)
    
    # Get product analytics for last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    analytics = ProductAnalytics.objects.filter(
        product=product,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    context = {
        'product': product,
        'analytics': analytics,
        'total_views': analytics.aggregate(total=Sum('page_views'))['total'] or 0,
        'total_sales': analytics.aggregate(total=Sum('revenue'))['total'] or 0,
        'total_units': analytics.aggregate(total=Sum('units_sold'))['total'] or 0,
        'conversion_rate': analytics.aggregate(avg=Avg('view_to_purchase_rate'))['avg'] or 0,
    }
    
    return render(request, 'analytics/product_analytics.html', context)


def products_analytics(request):
    """Products analytics overview page"""
    # Get top performing products
    top_products = ProductAnalytics.objects.select_related('product').filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).values('product__name', 'product__id', 'product__category__name').annotate(
        total_revenue=Sum('revenue'),
        total_units=Sum('units_sold'),
        total_views=Sum('page_views'),
        avg_conversion_rate=Avg('view_to_purchase_rate')
    ).order_by('-total_revenue')[:20]
    
    # Get product categories performance
    category_performance = ProductAnalytics.objects.select_related('product__category').filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).values('product__category__name').annotate(
        total_revenue=Sum('revenue'),
        total_units=Sum('units_sold'),
        total_views=Sum('page_views'),
        product_count=Count('product', distinct=True),
        avg_conversion_rate=Avg('view_to_purchase_rate')
    ).order_by('-total_revenue')
    
    # Get recent product analytics
    recent_analytics = ProductAnalytics.objects.select_related('product').filter(
        date__gte=timezone.now().date() - timedelta(days=7)
    ).order_by('-date', '-revenue')[:10]
    
    # Get all products for the dropdown
    all_products = Product.objects.select_related('category').all().order_by('name')
    
    context = {
        'top_products': top_products,
        'category_performance': category_performance,
        'recent_analytics': recent_analytics,
        'all_products': all_products,
    }
    
    return render(request, 'analytics/products_analytics.html', context)


def customer_analytics(request):
    """Customer analytics and segmentation"""
    # Get customer segments
    segments = CustomerAnalytics.objects.values('segment').annotate(
        count=Count('user', distinct=True),
        total_spent=Sum('total_spent'),
        avg_order_value=Avg('average_order_value')
    ).order_by('-total_spent')
    
    # Get top customers
    top_customers = CustomerAnalytics.objects.select_related('user').filter(
        date__gte=timezone.now().date() - timedelta(days=30)
    ).values('user__username', 'user__email').annotate(
        total_spent=Sum('total_spent'),
        total_orders=Sum('orders_count'),
        avg_order_value=Avg('average_order_value')
    ).order_by('-total_spent')[:20]
    
    context = {
        'segments': segments,
        'top_customers': top_customers,
    }
    
    return render(request, 'analytics/customer_analytics.html', context)
