from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='analytics_dashboard'),
    path('api/', views.analytics_api, name='analytics_api'),
    path('track/', views.track_event, name='track_event'),
    path('products/', views.products_analytics, name='products_analytics'),
    path('product/<int:product_id>/', views.product_analytics, name='product_analytics'),
    path('customers/', views.customer_analytics, name='customer_analytics'),
]