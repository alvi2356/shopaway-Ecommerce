from django.contrib import admin
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.db.models import Count, Sum

from .models import (
    AnalyticsEvent, SalesAnalytics, ProductAnalytics, 
    CustomerAnalytics, AnalyticsDashboard, AnalyticsWidget
)
from .admin_views import get_admin_dashboard_context


class CustomAdminSite(AdminSite):
    """Custom admin site with real analytics data"""
    
    def index(self, request, extra_context=None):
        """Custom admin index with real analytics data"""
        # Get real analytics data
        analytics_context = get_admin_dashboard_context()
        
        # Get default admin context
        context = super().index(request, extra_context)
        
        # Merge analytics data
        if context and 'context' in context:
            context['context'].update(analytics_context)
        else:
            context = analytics_context
        
        return TemplateResponse(request, 'admin/index.html', context)


# Register models with admin
@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'product_name', 'created_at']
    list_filter = ['event_type', 'created_at', 'user']
    search_fields = ['event_type', 'product_name', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_sales', 'total_orders', 'average_order_value', 'new_customers']
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'page_views', 'units_sold', 'revenue', 'view_to_purchase_rate']
    list_filter = ['date', 'product__category']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date', '-revenue']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'product__category')


@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'segment', 'total_spent', 'orders_count', 'page_views']
    list_filter = ['segment', 'date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date', '-total_spent']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_public', 'created_at']
    list_filter = ['is_default', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnalyticsWidget)
class AnalyticsWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard', 'widget_type', 'chart_type', 'is_visible']
    list_filter = ['widget_type', 'chart_type', 'is_visible', 'dashboard']
    search_fields = ['name', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dashboard')


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')
custom_admin_site.site_header = "ShopAway Analytics Admin"
custom_admin_site.site_title = "ShopAway Admin"
custom_admin_site.index_title = "Analytics Dashboard"
