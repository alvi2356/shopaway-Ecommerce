from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_widget, name='chat_widget'),
    path('start-session/', views.start_chat_session, name='start_chat_session'),
    path('send-message/', views.send_message, name='send_message'),
    path('session/<str:session_key>/messages/', views.get_session_messages, name='get_session_messages'),
    path('session/<str:session_key>/status/', views.check_session_status, name='check_session_status'),
    path('test-admin-message/<str:session_key>/', views.test_admin_message, name='test_admin_message'),
    path('test-server/', views.test_server, name='test_server'),
    path('test/', views.test_page, name='test_page'),
    path('admin/', views.admin_chat_dashboard, name='admin_chat_dashboard'),
    path('admin/session/<str:session_key>/', views.admin_chat_session, name='admin_chat_session'),
    path('admin/session/<str:session_key>/send/', views.admin_send_message, name='admin_send_message'),
    path('admin/session/<str:session_key>/assign/', views.assign_session_to_me, name='assign_session_to_me'),
    path('admin/session/<str:session_key>/close/', views.close_chat_session, name='close_chat_session'),
    path('admin/session/<str:session_key>/refresh/', views.refresh_session_messages, name='refresh_session_messages'),
    path('admin/unread-count/', views.get_unread_messages_count, name='get_unread_messages_count'),
]