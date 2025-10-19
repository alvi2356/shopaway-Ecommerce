from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from orders.models import Order, OrderItem
from products.models import Product, Category
from analytics.models import SalesAnalytics


class Command(BaseCommand):
    help = 'Generate sample analytics data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Generating sample analytics data...')
        
        # Generate sales analytics for last 7 days
        today = timezone.now().date()
        
        for i in range(7):
            date = today - timedelta(days=i)
            
            # Check if data already exists
            if SalesAnalytics.objects.filter(date=date).exists():
                continue
            
            # Generate sample data
            SalesAnalytics.objects.create(
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
            
            self.stdout.write(f'Generated data for {date}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully generated sample analytics data!')
        )
