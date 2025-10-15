from django.urls import path
from . import views
app_name = 'orders'
urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('confirm/<int:pk>/', views.confirm_order, name='confirm_order'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment/ssl/<int:order_id>/', views.ssl_payment_page, name='ssl_payment_page'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/fail/<int:order_id>/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/<int:order_id>/', views.payment_cancel, name='payment_cancel'),
]
