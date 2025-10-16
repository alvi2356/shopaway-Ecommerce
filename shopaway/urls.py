from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from shopaway.admin import admin_site
from products.views import home, search_results, search_suggestions

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', home, name='homepage'),
    path('search/', search_results, name='search_results'),
    path('search/suggestions/', search_suggestions, name='search_suggestions'),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('chat/', include('chat.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/pathao/', include('orders.api_urls')),
    path('health/', TemplateView.as_view(template_name='health.html')),
    path('about/', TemplateView.as_view(template_name='help/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='help/contact.html'), name='contact'),
    path('help/shipping/', TemplateView.as_view(template_name='help/shipping.html'), name='shipping_help'),
    path('help/returns/', TemplateView.as_view(template_name='help/returns.html'), name='returns_help'),
    path('help/faq/', TemplateView.as_view(template_name='help/faq.html'), name='faq_help'),
    path('mobile-test/', TemplateView.as_view(template_name='mobile_test_simple.html'), name='mobile_test'),
    path('mobile-demo/', TemplateView.as_view(template_name='mobile_demo.html'), name='mobile_demo'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
