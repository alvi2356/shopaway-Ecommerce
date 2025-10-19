from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
import json


class AnalyticsEvent(models.Model):
    """Track user interactions and events for analytics"""
    
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('checkout_start', 'Checkout Started'),
        ('purchase', 'Purchase'),
        ('search', 'Search'),
        ('category_view', 'Category View'),
        ('user_login', 'User Login'),
        ('user_register', 'User Registration'),
        ('newsletter_signup', 'Newsletter Signup'),
        ('contact_form', 'Contact Form'),
        ('custom', 'Custom Event'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    page_url = models.URLField(max_length=500, blank=True, null=True)
    page_title = models.CharField(max_length=200, blank=True, null=True)
    referrer = models.URLField(max_length=500, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Product-related data
    product_id = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    product_category = models.CharField(max_length=100, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    
    # Transaction data
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class SalesAnalytics(models.Model):
    """Daily sales analytics for performance tracking"""
    
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_products_sold = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    
    # Payment method breakdown
    cod_orders = models.IntegerField(default=0)
    online_orders = models.IntegerField(default=0)
    cod_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    online_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Order status breakdown
    pending_orders = models.IntegerField(default=0)
    confirmed_orders = models.IntegerField(default=0)
    shipped_orders = models.IntegerField(default=0)
    delivered_orders = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Sales Analytics - {self.date}"
    
    @classmethod
    def get_or_create_for_date(cls, date):
        """Get or create sales analytics for a specific date"""
        obj, created = cls.objects.get_or_create(date=date)
        if created:
            obj.calculate_metrics()
        return obj
    
    def calculate_metrics(self):
        """Calculate all metrics for this date"""
        from orders.models import Order, OrderItem
        
        # Get orders for this date
        orders = Order.objects.filter(created_at__date=self.date)
        order_items = OrderItem.objects.filter(order__created_at__date=self.date)
        
        # Basic metrics
        self.total_sales = orders.aggregate(total=Sum('total'))['total'] or 0
        self.total_orders = orders.count()
        self.total_products_sold = order_items.aggregate(total=Sum('qty'))['total'] or 0
        self.average_order_value = self.total_sales / self.total_orders if self.total_orders > 0 else 0
        
        # Customer metrics
        unique_customers = orders.values('user').distinct().count()
        new_customers = orders.filter(
            user__date_joined__date=self.date
        ).values('user').distinct().count()
        self.new_customers = new_customers
        self.returning_customers = unique_customers - new_customers
        
        # Payment method breakdown
        self.cod_orders = orders.filter(payment_method='cod').count()
        self.online_orders = orders.filter(payment_method='online').count()
        self.cod_revenue = orders.filter(payment_method='cod').aggregate(total=Sum('total'))['total'] or 0
        self.online_revenue = orders.filter(payment_method='online').aggregate(total=Sum('total'))['total'] or 0
        
        # Order status breakdown
        self.pending_orders = orders.filter(status='pending').count()
        self.confirmed_orders = orders.filter(status='confirmed').count()
        self.shipped_orders = orders.filter(status='shipped').count()
        self.delivered_orders = orders.filter(status='delivered').count()
        self.cancelled_orders = orders.filter(status='cancelled').count()
        
        self.save()


class ProductAnalytics(models.Model):
    """Product performance analytics"""
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    date = models.DateField()
    
    # Views and interactions
    page_views = models.IntegerField(default=0)
    add_to_cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    
    # Sales metrics
    units_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Conversion metrics
    view_to_cart_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cart_to_purchase_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    view_to_purchase_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date', '-revenue']
    
    def __str__(self):
        return f"{self.product.name} - {self.date}"
    
    def calculate_metrics(self):
        """Calculate conversion rates"""
        if self.page_views > 0:
            self.view_to_cart_rate = (self.add_to_cart_count / self.page_views) * 100
            self.view_to_purchase_rate = (self.purchase_count / self.page_views) * 100
        
        if self.add_to_cart_count > 0:
            self.cart_to_purchase_rate = (self.purchase_count / self.add_to_cart_count) * 100
        
        self.save()


class CustomerAnalytics(models.Model):
    """Customer behavior and segmentation analytics"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Activity metrics
    page_views = models.IntegerField(default=0)
    sessions = models.IntegerField(default=0)
    time_on_site = models.IntegerField(default=0)  # in seconds
    
    # Purchase behavior
    orders_count = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Product interactions
    products_viewed = models.IntegerField(default=0)
    products_added_to_cart = models.IntegerField(default=0)
    products_purchased = models.IntegerField(default=0)
    
    # Customer segment
    CUSTOMER_SEGMENTS = [
        ('new', 'New Customer'),
        ('regular', 'Regular Customer'),
        ('vip', 'VIP Customer'),
        ('at_risk', 'At Risk'),
        ('inactive', 'Inactive'),
    ]
    segment = models.CharField(max_length=20, choices=CUSTOMER_SEGMENTS, default='new')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', '-total_spent']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


class AnalyticsDashboard(models.Model):
    """Configurable analytics dashboard"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    # Dashboard configuration
    layout_config = models.JSONField(default=dict)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AnalyticsWidget(models.Model):
    """Configurable analytics widgets for dashboards"""
    
    WIDGET_TYPES = [
        ('metric', 'Metric Card'),
        ('chart', 'Chart'),
        ('table', 'Data Table'),
        ('gauge', 'Gauge'),
        ('progress', 'Progress Bar'),
        ('text', 'Text Widget'),
    ]
    
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
    ]
    
    dashboard = models.ForeignKey(AnalyticsDashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, null=True)
    
    # Data configuration
    data_source = models.CharField(max_length=100)
    query_filters = models.JSONField(default=dict)
    aggregation_type = models.CharField(max_length=50, default='sum')
    
    # Display configuration
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    width = models.IntegerField(default=6)  # Bootstrap grid columns
    height = models.IntegerField(default=4)  # Grid rows
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    
    # Styling
    color_scheme = models.CharField(max_length=50, default='default')
    show_legend = models.BooleanField(default=True)
    show_grid = models.BooleanField(default=True)
    
    # Behavior
    refresh_interval = models.IntegerField(default=300)  # seconds
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"
