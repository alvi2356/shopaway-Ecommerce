from django.shortcuts import redirect, render
from .cart import Cart
from products.models import Product

def add_to_cart(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        qty = int(request.POST.get('qty',1))
        cart = Cart(request)
        cart.add(sku, qty)
    next_url = request.POST.get('next') or request.GET.get('next') or '/'
    return redirect(next_url)

def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for sku, qty in cart.items():
        try:
            p = Product.objects.get(sku=sku)
            items.append({'product':p,'qty':qty,'subtotal': float(p.price)*int(qty)})
            total += float(p.price)*int(qty)
        except Product.DoesNotExist:
            continue
    return render(request, 'products/cart.html', {'items': items, 'total': total})

def buy_now(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        cart = Cart(request)
        cart.add(sku, 1)
    return redirect('cart_view')

def remove_from_cart(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        cart = Cart(request)
        cart.remove(sku)
    next_url = request.POST.get('next') or request.GET.get('next') or 'cart_view'
    return redirect(next_url)

def update_cart(request):
    if request.method == 'POST':
        sku = request.POST.get('sku')
        qty = int(request.POST.get('qty', 1))
        cart = Cart(request)
        if qty > 0:
            cart.cart[sku] = qty
            cart.session.modified = True
        else:
            cart.remove(sku)
    next_url = request.POST.get('next') or request.GET.get('next') or 'cart_view'
    return redirect(next_url)
