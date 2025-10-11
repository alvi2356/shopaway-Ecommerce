
# Shop Away - Django Starter (shopaway)

This is a starter Django web application scaffold for **Shop Away** implementing core features requested:
1. Order Management
2. Inventory Management
3. Payment Gateway integration hooks
4. Live Chat placeholder & integration points
5. Blog and News Section
6. Multi-user access (roles)
7. SEO-friendly templates & meta tags
8. Duplicate order detection logic (double entry prevention)
9. Performance & caching basics (whitenoise, template caching hooks)
10. Sales & Customer analytics skeleton (DRF endpoints + dashboard view)
11. Push notification hooks (service-worker + REST endpoint)
12. Advanced product filters (django-filter)
13. Responsive design (Bootstrap CDN - mobile-first)
14. Wishlist and Cart models & views
15. SMS integration hooks (provider-agnostic)
16. User-friendly admin with daily/monthly insights (admin actions & reports)

**Note**: This scaffold provides working local features and placeholders where external services (payment gateways, SMS, Pathao, Push, Live Chat) require credentials.
You will need to add your environment settings in a `.env` file and wire API keys for production features.

## How to run locally (quick)
1. Create a Python virtualenv and activate it.
2. Install requirements: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`
6. Visit http://127.0.0.1:8000/

## Files included
- Django project: shopaway/
- Apps: accounts, products, orders, inventory, blog, chat, analytics
- Example templates, static files, admin customizations, and API endpoints.

This is a starter template — extend as needed for payment gateways (e.g., SSLCommerz, Stripe), SMS providers, and Pathao integration.
