from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from orders.models import Order, OrderItem
from products.models import Product, Category
from analytics.models import (
    AnalyticsEvent, SalesAnalytics, ProductAnalytics, 
    CustomerAnalytics
)


class Command(BaseCommand):
    help = 'Populate analytics data with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate data for (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing analytics data before populating'
        )

    def handle(self, *args, **options):
        days = options['days']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing analytics data...')
            AnalyticsEvent.objects.all().delete()
            SalesAnalytics.objects.all().delete()
            ProductAnalytics.objects.all().delete()
            CustomerAnalytics.objects.all().delete()
        
        self.stdout.write(f'Generating analytics data for {days} days...')
        
        # Generate sales analytics for each day
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            self.generate_daily_analytics(current_date)
            current_date += timedelta(days=1)
        
        # Generate product analytics
        self.generate_product_analytics(start_date, end_date)
        
        # Generate customer analytics
        self.generate_customer_analytics(start_date, end_date)
        
        # Generate sample events
        self.generate_sample_events(start_date, end_date)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated analytics data for {days} days!'
            )
        )

    def generate_daily_analytics(self, date):
        """Generate sales analytics for a specific date"""
        # Get actual orders for this date
        orders = Order.objects.filter(created_at__date=date)
        
        if orders.exists():
            # Use real data
            sales_analytics = SalesAnalytics.get_or_create_for_date(date)
        else:
            # Generate sample data
            sales_analytics = SalesAnalytics.objects.create(
                date=date,
                total_sales=random.uniform(5000, 50000),
                total_orders=random.randint(10, 100),
                total_products_sold=random.randint(50, 500),
                average_order_value=random.uniform(500, 2000),
                new_customers=random.randint(2, 20),
                returning_customers=random.randint(5, 50),
                cod_orders=random.randint(5, 50),
                online_orders=random.randint(5, 50),
                cod_revenue=random.uniform(2000, 25000),
                online_revenue=random.uniform(3000, 25000),
                pending_orders=random.randint(2, 20),
                confirmed_orders=random.randint(3, 30),
                shipped_orders=random.randint(2, 25),
                delivered_orders=random.randint(1, 20),
                cancelled_orders=random.randint(0, 5),
            )

    def generate_product_analytics(self, start_date, end_date):
        """Generate product analytics data"""
        products = Product.objects.all()
        
        if not products.exists():
            self.stdout.write('No products found. Creating sample products...')
            self.create_sample_products()
            products = Product.objects.all()
        
        current_date = start_date
        while current_date <= end_date:
            for product in products:
                # Skip some days randomly to make data more realistic
                if random.random() < 0.3:  # 30% chance to skip
                    continue
                
                ProductAnalytics.objects.get_or_create(
                    product=product,
                    date=current_date,
                    defaults={
                        'page_views': random.randint(10, 200),
                        'add_to_cart_count': random.randint(2, 50),
                        'purchase_count': random.randint(1, 20),
                        'units_sold': random.randint(1, 30),
                        'revenue': random.uniform(100, 5000),
                    }
                )
            current_date += timedelta(days=1)

    def generate_customer_analytics(self, start_date, end_date):
        """Generate customer analytics data"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write('No users found. Creating sample users...')
            self.create_sample_users()
            users = User.objects.all()
        
        current_date = start_date
        while current_date <= end_date:
            for user in users:
                # Skip some days randomly
                if random.random() < 0.7:  # 70% chance to skip
                    continue
                
                CustomerAnalytics.objects.get_or_create(
                    user=user,
                    date=current_date,
                    defaults={
                        'page_views': random.randint(5, 100),
                        'sessions': random.randint(1, 5),
                        'time_on_site': random.randint(60, 3600),
                        'orders_count': random.randint(0, 3),
                        'total_spent': random.uniform(0, 2000),
                        'average_order_value': random.uniform(500, 1500),
                        'products_viewed': random.randint(1, 20),
                        'products_added_to_cart': random.randint(0, 10),
                        'products_purchased': random.randint(0, 5),
                        'segment': random.choice(['new', 'regular', 'vip', 'at_risk', 'inactive']),
                    }
                )
            current_date += timedelta(days=1)

    def generate_sample_events(self, start_date, end_date):
        """Generate sample analytics events"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        users = User.objects.all()
        products = Product.objects.all()
        
        event_types = [
            'page_view', 'product_view', 'add_to_cart', 
            'remove_from_cart', 'checkout_start', 'purchase',
            'search', 'category_view', 'user_login'
        ]
        
        current_date = start_date
        while current_date <= end_date:
            # Generate 50-200 events per day
            num_events = random.randint(50, 200)
            
            for _ in range(num_events):
                event_type = random.choice(event_types)
                user = random.choice(users) if users.exists() else None
                product = random.choice(products) if products.exists() else None
                
                AnalyticsEvent.objects.create(
                    event_type=event_type,
                    user=user,
                    session_id=f"session_{random.randint(1000, 9999)}",
                    page_url=f"https://shopaway.com/{random.choice(['products', 'categories', 'cart', 'checkout'])}",
                    page_title=f"Shop Away - {random.choice(['Products', 'Categories', 'Cart', 'Checkout'])}",
                    referrer=random.choice([
                        "https://google.com", "https://facebook.com", 
                        "https://twitter.com", "https://direct.com"
                    ]),
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    ip_address=f"192.168.1.{random.randint(1, 255)}",
                    product_id=str(product.id) if product else None,
                    product_name=product.name if product else None,
                    product_category=product.category.name if product and product.category else None,
                    product_price=product.price if product else None,
                    quantity=random.randint(1, 5),
                    transaction_id=f"txn_{random.randint(10000, 99999)}" if event_type == 'purchase' else None,
                    transaction_value=random.uniform(100, 2000) if event_type == 'purchase' else None,
                    metadata={
                        'source': random.choice(['organic', 'paid', 'social', 'direct']),
                        'device': random.choice(['desktop', 'mobile', 'tablet']),
                        'browser': random.choice(['chrome', 'firefox', 'safari', 'edge'])
                    }
                )
            
            current_date += timedelta(days=1)

    def create_sample_products(self):
        """Create sample products if none exist"""
        categories = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Clothing', 'slug': 'clothing'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Home & Garden', 'slug': 'home-garden'},
            {'name': 'Sports', 'slug': 'sports'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            
            # Create 5 products per category
            for i in range(5):
                Product.objects.get_or_create(
                    sku=f"{cat_data['slug']}-{i+1:03d}",
                    defaults={
                        'name': f"{cat_data['name']} Product {i+1}",
                        'slug': f"{cat_data['slug']}-product-{i+1}",
                        'description': f"High-quality {cat_data['name'].lower()} product {i+1}",
                        'price': random.uniform(100, 2000),
                        'category': category,
                        'stock': random.randint(10, 100),
                        'active': True,
                    }
                )

    def create_sample_users(self):
        """Create sample users if none exist"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        for i in range(10):
            username = f"user{i+1}"
            email = f"user{i+1}@example.com"
            
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=f"User {i+1}",
                    last_name="Test"
                )
