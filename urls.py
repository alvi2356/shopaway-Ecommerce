from django.urls import path, include

urlpatterns = [
    # ...existing code...
    path('chat/', include('chat.urls')),
]