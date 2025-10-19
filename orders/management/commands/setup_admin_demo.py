from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup demo data for admin panel testing'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up admin demo data...')
        )
        
        # Create superuser if doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@shopaway.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )
        
        # Create demo users
        demo_users = [
            {'username': 'manager', 'email': 'manager@shopaway.com', 'first_name': 'John', 'last_name': 'Manager'},
            {'username': 'staff', 'email': 'staff@shopaway.com', 'first_name': 'Jane', 'last_name': 'Staff'},
        ]
        
        for user_data in demo_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    password='demo123',
                    is_staff=True,
                    **user_data
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created staff user: {user_data["username"]}/demo123')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Admin demo setup completed!')
        )
        self.stdout.write(
            self.style.WARNING('Login credentials:')
        )
        self.stdout.write('  Superuser: admin/admin123')
        self.stdout.write('  Manager: manager/demo123')
        self.stdout.write('  Staff: staff/demo123')
