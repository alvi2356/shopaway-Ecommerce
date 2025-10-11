from django.shortcuts import render
from orders.models import Order
from django.db.models import Sum, Count
from django.utils import timezone


def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    total_sales_today = Order.objects.filter(created_at__date=today).aggregate(sum=Sum('total'))['sum'] or 0
    total_sales_month = Order.objects.filter(created_at__date__gte=month_start).aggregate(sum=Sum('total'))['sum'] or 0
    orders_today = Order.objects.filter(created_at__date=today).count()
    return render(request, 'analytics/dashboard.html', {
        'total_sales_today': total_sales_today,
        'total_sales_month': total_sales_month,
        'orders_today': orders_today
    })
