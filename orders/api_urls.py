from django.urls import path
from .views import PathaoWebhook

urlpatterns = [
    path('webhook/', PathaoWebhook.as_view(), name='pathao_webhook'),
]
