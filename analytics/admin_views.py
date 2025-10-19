from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg

from orders.models import Order, OrderItem
from products.models import Product
from analytics.models import SalesAnalytics


@staff_member_required
def admin_dashboard_data(request):
    """Provide real analytics data for admin dashboard"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Get today's sales analytics
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    sales_yesterday = SalesAnalytics.get_or_create_for_date(yesterday)
    
    # Calculate growth rates
    sales_growth = 0
    if sales_yesterday.total_sales > 0:
        sales_growth = ((sales_today.total_sales - sales_yesterday.total_sales) / sales_yesterday.total_sales) * 100
    
    orders_growth = 0
    if sales_yesterday.total_orders > 0:
        orders_growth = ((sales_today.total_orders - sales_yesterday.total_orders) / sales_yesterday.total_orders) * 100
    
    # Get recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Get sales data for last 7 days
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_sales = SalesAnalytics.objects.filter(date=date).first()
        sales_data.append(float(daily_sales.total_sales) if daily_sales else 0)
    sales_data.reverse()  # Show oldest to newest
    
    # Get pending orders count
    pending_orders = Order.objects.filter(status='pending').count()
    
    context = {
        'today_sales': sales_today.total_sales,
        'today_orders': sales_today.total_orders,
        'products_sold_today': sales_today.total_products_sold,
        'avg_order_value': sales_today.average_order_value,
        'sales_growth': round(sales_growth, 1),
        'orders_growth': round(orders_growth, 1),
        'recent_orders': recent_orders,
        'sales_data': sales_data,
        'pending_orders': pending_orders,
        'cod_orders': sales_today.cod_orders,
        'online_orders': sales_today.online_orders,
    }
    
    return context


def get_admin_dashboard_context():
    """Get context data for admin dashboard - can be called from admin views"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Get today's sales analytics
    sales_today = SalesAnalytics.get_or_create_for_date(today)
    sales_yesterday = SalesAnalytics.get_or_create_for_date(yesterday)
    
    # Calculate growth rates
    sales_growth = 0
    if sales_yesterday.total_sales > 0:
        sales_growth = ((sales_today.total_sales - sales_yesterday.total_sales) / sales_yesterday.total_sales) * 100
    
    orders_growth = 0
    if sales_yesterday.total_orders > 0:
        orders_growth = ((sales_today.total_orders - sales_yesterday.total_orders) / sales_yesterday.total_orders) * 100
    
    # Get recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Get sales data for last 7 days
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_sales = SalesAnalytics.objects.filter(date=date).first()
        sales_data.append(float(daily_sales.total_sales) if daily_sales else 0)
    sales_data.reverse()  # Show oldest to newest
    
    # Get pending orders count
    pending_orders = Order.objects.filter(status='pending').count()
    
    return {
        'today_sales': sales_today.total_sales,
        'today_orders': sales_today.total_orders,
        'products_sold_today': sales_today.total_products_sold,
        'avg_order_value': sales_today.average_order_value,
        'sales_growth': round(sales_growth, 1),
        'orders_growth': round(orders_growth, 1),
        'recent_orders': recent_orders,
        'sales_data': sales_data,
        'pending_orders': pending_orders,
        'cod_orders': sales_today.cod_orders,
        'online_orders': sales_today.online_orders,
    }
