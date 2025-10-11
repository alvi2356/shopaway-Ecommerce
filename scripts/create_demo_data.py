from django.contrib.auth import get_user_model
from products.models import Category, Product

def run():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin','admin@example.com','admin')
    c, _ = Category.objects.get_or_create(name='Default', slug='default')
    for i in range(1,11):
        Product.objects.get_or_create(sku=f'SKU{i}', name=f'Product {i}', slug=f'product-{i}', price=100+i*10, stock=10, category=c)

if __name__ == '__main__':
    run()
