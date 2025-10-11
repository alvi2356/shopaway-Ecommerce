from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Q
import json
import uuid
from .models import ChatSession, ChatMessage, ChatNotification


def chat_widget(request):
    """Render the chat widget page"""
    return render(request, 'chat/widget.html')


@csrf_exempt
@require_http_methods(["POST"])
def start_chat_session(request):
    """Start a new chat session with user name and email"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        
        if not name or not email:
            return JsonResponse({'error': 'Name and email are required'}, status=400)
        
        # Create new chat session
        session_key = str(uuid.uuid4())
        session = ChatSession.objects.create(
            session_key=session_key,
            user_name=name,
            user_email=email
        )
        
        # Create initial welcome message
        ChatMessage.objects.create(
            session=session,
            message="Hi! How can I help you today?",
            is_staff_reply=True
        )
        
        return JsonResponse({
            'session_key': session_key,
            'name': name,
            'email': email
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    Send a message in a chat session from user side.
    This view handles user message creation, database storage, and WebSocket broadcasting.
    """
    try:
        data = json.loads(request.body)
        session_key = data.get('session_key')
        message = data.get('message', '').strip()
        
        if not session_key or not message:
            return JsonResponse({'error': 'Session key and message are required'}, status=400)
        
        # Get the chat session
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Create and save the user message to database
        chat_message = ChatMessage.objects.create(
            session=session,
            message=message,
            is_staff_reply=False
        )
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])
        
        print(f"💾 User message saved to database: {message}")
        
        # Broadcast message via WebSocket to all connected clients
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{session_key}'
        
        print(f"🔔 Broadcasting user message to room: {room_group_name}")
        
        try:
            # Send message to WebSocket group for real-time updates
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'is_staff_reply': False,
                    'timestamp': chat_message.timestamp.isoformat(),
                    'message_id': chat_message.id,
                }
            )
            print(f"✅ User message broadcasted successfully via WebSocket")
        except Exception as e:
            print(f"❌ WebSocket broadcasting failed: {e}")
            # Continue execution even if WebSocket fails - message is saved in DB
        
        # Create notifications for all staff users about new user message
        from django.contrib.auth.models import User
        staff_users = User.objects.filter(is_staff=True)
        for staff_user in staff_users:
            ChatNotification.objects.get_or_create(
                session=session,
                staff_user=staff_user,
                defaults={'is_read': False}
            )
        
        print(f"📧 Notifications created for {staff_users.count()} staff users")
        
        # Return success response
        return JsonResponse({
            'status': 'success',
            'message_id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in send_message: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def admin_chat_dashboard(request):
    """Admin dashboard for managing chat sessions"""
    active_sessions = ChatSession.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'chat/admin_dashboard.html', {
        'active_sessions': active_sessions
    })


@staff_member_required
def admin_chat_session(request, session_key):
    """Admin view for a specific chat session"""
    session = get_object_or_404(ChatSession, session_key=session_key)
    messages = session.messages.all().order_by('timestamp')
    
    # Mark notifications as read for current staff user
    ChatNotification.objects.filter(
        session=session,
        staff_user=request.user
    ).update(is_read=True)
    
    return render(request, 'chat/admin_session.html', {
        'session': session,
        'messages': messages
    })


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_send_message(request, session_key):
    """
    Admin sends a message to a chat session.
    This view handles admin message creation, database storage, and WebSocket broadcasting.
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get the chat session
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Create and save the staff message to database
        chat_message = ChatMessage.objects.create(
            session=session,
            message=message,
            is_staff_reply=True,
            sender=request.user
        )
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])
        
        print(f"💾 Admin message saved to database: {message}")
        
        # Broadcast message via WebSocket to all connected clients
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{session_key}'
        
        print(f"🔔 Broadcasting admin message to room: {room_group_name}")
        
        try:
            # Send message to WebSocket group for real-time updates
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'is_staff_reply': True,
                    'timestamp': chat_message.timestamp.isoformat(),
                    'message_id': chat_message.id,
                }
            )
            print(f"✅ Admin message broadcasted successfully via WebSocket")
        except Exception as e:
            print(f"❌ WebSocket broadcasting failed: {e}")
            # Continue execution even if WebSocket fails - message is saved in DB
        
        # Return success response
        return JsonResponse({
            'status': 'success',
            'message_id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in admin_send_message: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def get_unread_messages_count(request):
    """Get count of unread messages for admin"""
    unread_count = ChatNotification.objects.filter(
        staff_user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': unread_count})


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def assign_session_to_me(request, session_key):
    """
    Assign a chat session to the current admin user.
    This allows admins to claim ownership of chat sessions.
    """
    try:
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Assign session to current user
        session.assigned_to = request.user
        session.save(update_fields=['assigned_to'])
        
        print(f"👤 Session {session_key} assigned to {request.user.username}")
        
        return JsonResponse({
            'status': 'success',
            'message': f'Session assigned to {request.user.username}',
            'assigned_to': request.user.username
        })
        
    except Exception as e:
        print(f"❌ Error assigning session: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def close_chat_session(request, session_key):
    """
    Close a chat session.
    This marks the session as inactive and prevents new messages.
    """
    try:
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Mark session as inactive
        session.is_active = False
        session.save(update_fields=['is_active'])
        
        print(f"🔒 Session {session_key} closed by {request.user.username}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Session closed successfully'
        })
        
    except Exception as e:
        print(f"❌ Error closing session: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def refresh_session_messages(request, session_key):
    """
    Refresh messages for a chat session.
    This forces a reload of all messages from the database.
    """
    try:
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Get all messages for this session
        messages = session.messages.all().order_by('timestamp')
        
        # Format messages for response
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'message': msg.message,
                'is_staff_reply': msg.is_staff_reply,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read,
                'sender_name': session.user_name if not msg.is_staff_reply else 'Staff'
            })
        
        print(f"🔄 Refreshed {len(messages_data)} messages for session {session_key}")
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data,
            'message_count': len(messages_data)
        })
        
    except Exception as e:
        print(f"❌ Error refreshing messages: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_session_messages(request, session_key):
    """
    Get all messages for a chat session.
    This view retrieves all messages from the database for a specific session.
    """
    try:
        # Get the chat session
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Retrieve all messages for this session, ordered by timestamp
        messages = session.messages.all().order_by('timestamp')
        
        print(f"📨 Retrieving {messages.count()} messages for session: {session_key}")
        
        # Format messages for JSON response
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'message': msg.message,
                'is_staff_reply': msg.is_staff_reply,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read,
                'sender_name': session.user_name if not msg.is_staff_reply else 'Staff'
            })
        
        print(f"✅ Successfully retrieved {len(messages_data)} messages")
        
        return JsonResponse({
            'messages': messages_data,
            'session_info': {
                'user_name': session.user_name,
                'user_email': session.user_email,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'is_active': session.is_active,
                'assigned_to': session.assigned_to.username if session.assigned_to else None
            }
        })
        
    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_session_status(request, session_key):
    """
    Check the status of a chat session.
    This endpoint allows the frontend to check if a session is still active.
    """
    try:
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        return JsonResponse({
            'session_key': session_key,
            'is_active': session.is_active,
            'assigned_to': session.assigned_to.username if session.assigned_to else None,
            'user_name': session.user_name,
            'user_email': session.user_email,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error checking session status: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_admin_message(request, session_key):
    """Test endpoint to send admin message for debugging"""
    try:
        session = get_object_or_404(ChatSession, session_key=session_key)
        
        # Create test admin message
        chat_message = ChatMessage.objects.create(
            session=session,
            message="Test admin message from debug endpoint",
            is_staff_reply=True
        )
        
        # Broadcast message via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{session_key}'
        
        print(f"🧪 TEST: Broadcasting test admin message to room: {room_group_name}")
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': chat_message.message,
                'is_staff_reply': True,
                'timestamp': chat_message.timestamp.isoformat(),
            }
        )
        
        return JsonResponse({'status': 'success', 'message': 'Test message sent'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def test_server(request):
    """Simple test endpoint to verify server is running"""
    return JsonResponse({
        'status': 'success',
        'message': 'Server is running',
        'timestamp': timezone.now().isoformat()
    })


def test_page(request):
    """Test page for debugging chat functionality"""
    return render(request, 'chat/test.html')