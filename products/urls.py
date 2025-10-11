from django.urls import path
from . import views, cart_views
urlpatterns = [
    path('all/', views.all_products, name='all_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/add/', cart_views.add_to_cart, name='cart_add'),
    path('cart/', cart_views.view_cart, name='cart_view'),
    path('cart/buy-now/', cart_views.buy_now, name='buy_now'),
    path('cart/remove/', cart_views.remove_from_cart, name='cart_remove'),
    path('cart/update/', cart_views.update_cart, name='cart_update'),
]
