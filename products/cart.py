# session-based cart helper
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    def add(self, sku, qty=1):
        self.cart[sku] = self.cart.get(sku, 0) + int(qty)
        self.session.modified = True
    def remove(self, sku):
        if sku in self.cart:
            del self.cart[sku]
            self.session.modified = True
    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True
