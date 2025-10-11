from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

try:
    from products.models import Product
except Exception:  # app may not be migrated yet
    Product = None

try:
    from orders.models import Order
except Exception:
    Order = None


class ShopAwayAdminSite(admin.AdminSite):
    site_header = "ShopAway"
    site_title = "ShopAway Admin"
    index_title = "Dashboard"
    index_template = "admin/index.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("", self.admin_view(self.dashboard_view), name="index"),
        ]
        return custom + urls

    def dashboard_view(self, request):
        context = dict(self.each_context(request))
        User = get_user_model()
        context["users_count"] = User.objects.count()
        context["products_count"] = Product.objects.count() if Product else 0
        if Order:
            since = timezone.now() - timezone.timedelta(days=30)
            qs = Order.objects.filter(created_at__gte=since)
            context["orders_last_30"] = qs.count()
            revenue = 0
            try:
                revenue = sum(getattr(o, "total", 0) for o in qs)
            except Exception:
                revenue = 0
            context["revenue_last_30"] = revenue
        else:
            context.update({"orders_last_30": 0, "revenue_last_30": 0})
        return TemplateResponse(request, "admin/index.html", context)


admin_site = ShopAwayAdminSite(name="shopaway_admin")
# Load all app admin modules into the default site registry, then mirror them to our custom site
try:
    admin.autodiscover()
    for model, model_admin in admin.site._registry.items():
        try:
            admin_site.register(model, model_admin.__class__)
        except admin.sites.AlreadyRegistered:
            continue
except Exception:
    # In migrations/startup, fail gracefully; the dashboard will still render
    pass
