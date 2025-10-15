from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, CourierLog
from products.models import Product
from django.utils import timezone
import hashlib
from django.core.mail import send_mail
from django.conf import settings

# DRF webhook
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Simple double-entry detection: hash of name+phone+address+total rounded
def make_double_hash(name, phone, address, total):
    key = f"{name}|{phone}|{address}|{round(float(total),2)}"
    return hashlib.sha256(key.encode()).hexdigest()

@require_POST
def create_order(request):
    data = request.POST
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    email = data.get('email')
    payment_method = data.get('payment_method', 'cod')
    
    cart_items = request.session.get('cart', {})
    if not cart_items:
        return render(request, 'orders/no_cart.html')
    
    total = 0
    for sku, qty in cart_items.items():
        try:
            p = Product.objects.get(sku=sku)
            total += float(p.price) * int(qty)
        except Product.DoesNotExist:
            continue
    
    double_hash = make_double_hash(name, phone, address, total)
    if Order.objects.filter(double_entry_hash=double_hash, created_at__gte=timezone.now()-timezone.timedelta(hours=24)).exists():
        return render(request, 'orders/duplicate.html')
    
    # Create order with payment method
    order = Order.objects.create(
        name=name, 
        phone=phone, 
        address=address, 
        email=email,
        total=total, 
        double_entry_hash=double_hash,
        payment_method=payment_method,
        payment_status='pending' if payment_method == 'online' else 'paid'
    )
    
    for sku, qty in cart_items.items():
        try:
            p = Product.objects.get(sku=sku)
            OrderItem.objects.create(order=order, product=p, qty=qty, price=p.price)
            p.stock = max(0, p.stock - int(qty))
            p.save()
        except Product.DoesNotExist:
            continue
    
    # Clear cart
    request.session['cart'] = {}
    
    try:
        send_mail(f'Order Confirmation #{order.id}', f'Thanks for your order. Reference: {order.id}', settings.EMAIL_HOST_USER, [email])
    except Exception:
        pass
    
    request.session['last_order_id'] = order.id
    
    # Handle payment method
    if payment_method == 'online':
        return redirect('orders:process_payment', order_id=order.id)
    else:
        return redirect('orders:confirm_order', pk=order.id)

def confirm_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/confirm.html', {'order': order})

def process_payment(request, order_id):
    """Process online payment with SSL Commerz."""
    order = get_object_or_404(Order, pk=order_id)
    
    if order.payment_method != 'online':
        return redirect('orders:confirm_order', pk=order.id)
    
    try:
        from .ssl_commerz import SSLCommerzClient
        
        ssl_client = SSLCommerzClient()
        payment_data = ssl_client.create_payment_session(order, request)
        payment_result = ssl_client.initiate_payment(payment_data)
        
        if payment_result.get('status') == 'success':
            if 'redirect_url' in payment_result:
                return redirect(payment_result['redirect_url'])
            else:
                # Handle API response - show SSL Commerz style payment form
                return render(request, 'orders/ssl_payment.html', {
                    'order': order,
                    'payment_data': payment_data,
                    'payment_result': payment_result
                })
        else:
            # If SSL Commerz fails, show SSL Commerz style fallback
            return render(request, 'orders/ssl_payment.html', {
                'order': order,
                'error': payment_result.get('message', 'Payment gateway temporarily unavailable')
            })
    except Exception as e:
        # If there's any error, show SSL Commerz style fallback
        return render(request, 'orders/ssl_payment.html', {
            'order': order,
            'error': f'Payment gateway error: {str(e)}'
        })

def payment_success(request, order_id):
    """Handle successful payment."""
    order = get_object_or_404(Order, pk=order_id)
    
    from .ssl_commerz import SSLCommerzClient
    ssl_client = SSLCommerzClient()
    verification_result = ssl_client.verify_payment(request)
    
    if verification_result.get('status') == 'success':
        # Update order payment status
        order.payment_status = 'paid'
        order.payment_transaction_id = request.GET.get('tran_id')
        order.payment_gateway_response = verification_result.get('data')
        order.save()
        
        return render(request, 'orders/payment_success.html', {
            'order': order,
            'transaction_id': request.GET.get('tran_id')
        })
    else:
        return render(request, 'orders/payment_error.html', {
            'order': order,
            'error': 'Payment verification failed'
        })

def payment_fail(request, order_id):
    """Handle failed payment."""
    order = get_object_or_404(Order, pk=order_id)
    order.payment_status = 'failed'
    order.save()
    
    return render(request, 'orders/payment_fail.html', {'order': order})

def payment_cancel(request, order_id):
    """Handle cancelled payment."""
    order = get_object_or_404(Order, pk=order_id)
    order.payment_status = 'cancelled'
    order.save()
    
    return render(request, 'orders/payment_cancel.html', {'order': order})

def ssl_payment_page(request, order_id):
    """Direct SSL Commerz style payment page."""
    order = get_object_or_404(Order, pk=order_id)
    
    if order.payment_method != 'online':
        return redirect('orders:confirm_order', pk=order.id)
    
    return render(request, 'orders/ssl_payment.html', {
        'order': order
    })


@method_decorator(csrf_exempt, name='dispatch')
class PathaoWebhook(APIView):
    """Webhook receiver for Pathao courier updates.

    Security: expects 'X-Pathao-Token' header to match settings.PATHAO['WEBHOOK_TOKEN'].
    Payload shape may vary; we attempt best-effort parsing for order reference & status.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        token = request.headers.get('X-Pathao-Token') or request.META.get('HTTP_X_PATHAO_TOKEN')
        expected = (getattr(settings, 'PATHAO', {}) or {}).get('WEBHOOK_TOKEN')
        if not expected or token != expected:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        payload = request.data or {}

        # Attempt to find the order: by merchant_order_id or order_id mapping
        merchant_order_id = payload.get('merchant_order_id') or payload.get('data', {}).get('merchant_order_id')
        pathao_order_id = payload.get('order_id') or payload.get('data', {}).get('order_id')
        new_status = payload.get('status') or payload.get('data', {}).get('status')

        order = None
        if merchant_order_id:
            try:
                order = Order.objects.get(pk=int(merchant_order_id))
            except Exception:
                order = None
        if not order and pathao_order_id:
            order = Order.objects.filter(pathao_order_id=str(pathao_order_id)).first()

        if not order:
            # Unknown order; accept to avoid retries, and avoid writing a log requiring an order FK.
            return Response({'detail': 'Order not found'}, status=status.HTTP_202_ACCEPTED)

        # Update order fields
        if pathao_order_id and not order.pathao_order_id:
            order.pathao_order_id = str(pathao_order_id)
        if new_status:
            order.pathao_status = new_status
        order.pathao_response = payload
        order.save(update_fields=['pathao_order_id', 'pathao_status', 'pathao_response'])

        CourierLog.objects.create(order=order, action='webhook', raw_payload=payload)

        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)
