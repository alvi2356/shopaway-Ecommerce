# Chat models removed from admin panel
# from django.contrib import admin
# from .models import ChatSession, ChatMessage, ChatNotification

# Chat admin classes commented out to remove from admin panel
# @admin.register(ChatSession)
# class ChatSessionAdmin(admin.ModelAdmin):
#     list_display = ['user_name', 'user_email', 'is_active', 'created_at', 'assigned_to']
#     list_filter = ['is_active', 'created_at', 'assigned_to']
#     search_fields = ['user_name', 'user_email', 'session_key']
#     readonly_fields = ['session_key', 'created_at', 'updated_at']
#     list_editable = ['is_active', 'assigned_to']
#     
#     fieldsets = (
#         ('Session Info', {
#             'fields': ('session_key', 'user_name', 'user_email', 'is_active')
#         }),
#         ('Assignment', {
#             'fields': ('assigned_to',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )

# @admin.register(ChatMessage)
# class ChatMessageAdmin(admin.ModelAdmin):
#     list_display = ['session', 'message_preview', 'is_staff_reply', 'sender', 'timestamp', 'is_read']
#     list_filter = ['is_staff_reply', 'is_read', 'timestamp', 'sender']
#     search_fields = ['message', 'session__user_name', 'session__user_email']
#     readonly_fields = ['timestamp']
#     list_editable = ['is_read']
#     
#     def message_preview(self, obj):
#         return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
#     message_preview.short_description = 'Message'

# @admin.register(ChatNotification)
# class ChatNotificationAdmin(admin.ModelAdmin):
#     list_display = ['session', 'staff_user', 'is_read', 'created_at']
#     list_filter = ['is_read', 'created_at', 'staff_user']
#     search_fields = ['session__user_name', 'session__user_email', 'staff_user__username']
#     list_editable = ['is_read']