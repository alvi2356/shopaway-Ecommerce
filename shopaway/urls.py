from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from shopaway.admin import admin_site
from products.views import home

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', home, name='homepage'),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('chat/', include('chat.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/pathao/', include('orders.api_urls')),
    path('health/', TemplateView.as_view(template_name='health.html')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
