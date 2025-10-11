from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class ChatSession(models.Model):
    """
    Represents a chat session between a user and support staff.
    This model stores session information and tracks the conversation state.
    """
    session_key = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_chats')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
    
    def __str__(self):
        return f"Chat with {self.user_name} ({self.user_email})"
    
    def get_latest_message(self):
        """Get the latest message in this session"""
        return self.messages.last()
    
    def get_unread_count(self):
        """Get count of unread messages for staff"""
        return self.messages.filter(is_staff_reply=False, is_read=False).count()


class ChatMessage(models.Model):
    """
    Represents individual messages in a chat session.
    This model stores all messages with proper relationships and metadata.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['is_staff_reply', 'timestamp']),
        ]
    
    def __str__(self):
        sender_name = "Staff" if self.is_staff_reply else self.session.user_name
        return f"{sender_name}: {self.message[:50]}..."
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])


class ChatNotification(models.Model):
    """
    Notifications for staff about new messages.
    This ensures staff are notified of new user messages.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='notifications')
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['session', 'staff_user']
        verbose_name = "Chat Notification"
        verbose_name_plural = "Chat Notifications"
    
    def __str__(self):
        return f"Notification for {self.staff_user.username} - {self.session.user_name}"