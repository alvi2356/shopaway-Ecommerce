def cart_context(request):
    """Add cart information to all templates"""
    cart = request.session.get('cart', {})
    cart_count = 0
    cart_needs_cleanup = False
    
    if cart:
        for sku, value in cart.items():
            if isinstance(value, int):
                # Normal case: value is quantity (integer)
                cart_count += value
            elif isinstance(value, dict) and 'qty' in value:
                # Corrupted case: value is a dictionary with 'qty' key
                cart_count += value.get('qty', 0)
                cart_needs_cleanup = True
            else:
                # Fallback: treat as 1 if it's neither int nor dict with qty
                cart_count += 1
                cart_needs_cleanup = True
        
        # Clean up corrupted cart data
        if cart_needs_cleanup:
            cleaned_cart = {}
            for sku, value in cart.items():
                if isinstance(value, int):
                    cleaned_cart[sku] = value
                elif isinstance(value, dict) and 'qty' in value:
                    cleaned_cart[sku] = value.get('qty', 0)
                else:
                    cleaned_cart[sku] = 1
            request.session['cart'] = cleaned_cart
            request.session.modified = True
    
    return {
        'cart_count': cart_count
    }
