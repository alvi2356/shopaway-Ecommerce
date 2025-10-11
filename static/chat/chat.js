/**
 * Chat Widget JavaScript - Fixed Version
 * 
 * This file handles all frontend chat functionality including:
 * - WebSocket connections for real-time messaging
 * - Message display and formatting
 * - Database persistence and message loading
 * - Fallback mechanisms for reliable message delivery
 */

// Global variables for chat functionality
let chatSessionKey = null;
let chatSocket = null;
let isConnected = false;
let messagePollingInterval = null;

/**
 * Initialize chat functionality when DOM is loaded
 * This sets up the chat widget and restores any existing session
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing chat widget...');
    
    // Check for existing session in localStorage
    const savedSession = localStorage.getItem('chat_session_key');
    const savedName = localStorage.getItem('chat_name');
    const savedEmail = localStorage.getItem('chat_email');
    
    if (savedSession && savedName && savedEmail) {
        console.log('📱 Found existing session:', savedSession);
        chatSessionKey = savedSession;
        
        // Don't auto-open chat - let user click the chat button
        // Just prepare the session for when they do open it
        console.log('💬 Session ready - user can open chat when needed');
    }
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('✅ Chat widget initialized');
});

/**
 * Setup all event listeners for chat functionality
 */
function setupEventListeners() {
    // Chat start form submission
    const chatStartForm = document.getElementById('chat-start-form');
    if (chatStartForm) {
        chatStartForm.addEventListener('submit', handleChatStart);
    }
    
    // Send button click
    const sendBtn = document.getElementById('chat-send-btn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    // Enter key in message input
    const messageInput = document.getElementById('chat-message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

/**
 * Handle chat session start
 * This creates a new chat session and connects to WebSocket
 */
async function handleChatStart(e) {
    e.preventDefault();
    
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    
    if (!name || !email) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        console.log('🚀 Starting new chat session...');
        
        const response = await fetch('/chat/start-session/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ name, email })
        });
        
        const data = await response.json();
        
        if (data.session_key) {
            console.log('✅ Chat session created:', data.session_key);
            
            // Store session info in localStorage
            chatSessionKey = data.session_key;
            localStorage.setItem('chat_session_key', chatSessionKey);
            localStorage.setItem('chat_name', name);
            localStorage.setItem('chat_email', email);
            
            // Show chat messages interface
            showChatMessages();
            
            // Connect to WebSocket
            connectWebSocket();
            
            // Start polling for messages
            startMessagePolling();
            
        } else {
            console.error('❌ Failed to create chat session:', data.error);
            alert('Failed to start chat. Please try again.');
        }
        
    } catch (error) {
        console.error('❌ Error starting chat session:', error);
        alert('Failed to start chat. Please try again.');
    }
}

/**
 * Show chat messages interface
 * This switches from pre-chat form to chat messages display
 */
function showChatMessages() {
    const preChatForm = document.getElementById('pre-chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const chatFooter = document.getElementById('chat-footer');
    
    // Hide pre-chat form
    if (preChatForm) preChatForm.style.display = 'none';
    
    // Show chat messages container
    if (chatMessages) {
        chatMessages.style.display = 'block';
        chatMessages.style.flex = '1';
        chatMessages.style.overflowY = 'auto';
        chatMessages.style.padding = '15px';
        chatMessages.style.background = '#f8f9fa';
    }
    
    // Show chat footer with input
    if (chatFooter) chatFooter.style.display = 'block';
    
    // Enable input and send button
    const messageInput = document.getElementById('chat-message-input');
    const sendBtn = document.getElementById('chat-send-btn');
    if (messageInput) messageInput.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
    
    console.log('✅ Chat messages interface shown');
}

/**
 * Connect to WebSocket for real-time messaging
 * This establishes a WebSocket connection for instant message delivery
 */
function connectWebSocket() {
    if (!chatSessionKey) {
        console.log('❌ No session key available for WebSocket connection');
        return;
    }
    
    console.log('🔌 Connecting to WebSocket for session:', chatSessionKey);
    
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_url = `${ws_scheme}://${window.location.host}/ws/chat/${chatSessionKey}/`;
    
    try {
        chatSocket = new WebSocket(ws_url);
        
        chatSocket.onopen = function() {
            isConnected = true;
            console.log('✅ WebSocket connected for session:', chatSessionKey);
        };
        
        chatSocket.onmessage = function(e) {
            console.log('📨 WebSocket message received:', e.data);
            try {
                const data = JSON.parse(e.data);
                console.log('📨 Parsed message data:', data);
                
                // Add message to chat display
                addMessageToChat(data.message, data.is_staff_reply, data.timestamp);
                
                if (data.is_staff_reply) {
                    console.log('🎯 ADMIN MESSAGE RECEIVED IN FRONTEND!');
                }
                
            } catch (error) {
                console.error('❌ Error parsing WebSocket message:', error);
            }
        };
        
        chatSocket.onclose = function(event) {
            isConnected = false;
            console.log('❌ WebSocket disconnected:', event.code, event.reason);
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (chatSessionKey) {
                    console.log('🔄 Attempting to reconnect WebSocket...');
                    connectWebSocket();
                }
            }, 3000);
        };
        
        chatSocket.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
            isConnected = false;
        };
        
    } catch (error) {
        console.error('❌ Failed to create WebSocket connection:', error);
        isConnected = false;
    }
}

/**
 * Send a message in the chat
 * This handles both WebSocket and HTTP fallback for message sending
 */
function sendMessage() {
    const messageInput = document.getElementById('chat-message-input');
    if (!messageInput) {
        console.error('❌ Message input not found');
        return;
    }
    
    // Check if input is disabled (session closed)
    if (messageInput.disabled) {
        console.log('⚠️ Chat session is closed, cannot send message');
        return;
    }
    
    const message = messageInput.value.trim();
    if (!message) {
        console.log('⚠️ No message to send');
        return;
    }
    
    if (!chatSessionKey) {
        console.error('❌ No session key available');
        alert('Please start a chat session first.');
        return;
    }
    
    console.log('📤 Sending message:', message);
    
    // Add message to UI immediately for better UX
    addMessageToChat(message, false, new Date().toISOString());
    
    // Clear input
    messageInput.value = '';
    messageInput.focus();
    
    // Try WebSocket first, then HTTP fallback
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN && isConnected) {
        console.log('🌐 Sending via WebSocket...');
        try {
            chatSocket.send(JSON.stringify({ 
                message: message, 
                is_staff_reply: false 
            }));
            console.log('✅ Message sent via WebSocket');
        } catch (error) {
            console.error('❌ WebSocket send error:', error);
            sendMessageViaHTTP(message);
        }
    } else {
        console.log('🔄 WebSocket not available, using HTTP fallback');
        sendMessageViaHTTP(message);
    }
}

/**
 * Send message via HTTP as fallback
 * This ensures message delivery even if WebSocket fails
 */
function sendMessageViaHTTP(message) {
    console.log('📡 Sending message via HTTP...');
    
    fetch('/chat/send-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            session_key: chatSessionKey,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('✅ Message sent via HTTP');
        } else {
            console.error('❌ HTTP send failed:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ HTTP send error:', error);
    });
}

/**
 * Add message to chat display
 * This creates and displays a message in the chat interface
 */
function addMessageToChat(message, isStaffReply, timestamp) {
    console.log('📝 Adding message to chat:', { message, isStaffReply, timestamp });
    
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) {
        console.error('❌ Chat messages container not found');
        return;
    }
    
    // Ensure container is visible and properly styled
    messagesContainer.style.display = 'block';
    messagesContainer.style.flex = '1';
    messagesContainer.style.overflowY = 'auto';
    messagesContainer.style.padding = '15px';
    messagesContainer.style.background = '#f8f9fa';
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isStaffReply ? 'staff' : 'user'}`;
    messageDiv.style.display = 'block';
    messageDiv.style.marginBottom = '15px';
    messageDiv.style.animation = 'fadeIn 0.3s ease-out';
    
    // Create message bubble
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    messageBubble.textContent = message;
    messageBubble.style.maxWidth = '80%';
    messageBubble.style.padding = '10px 15px';
    messageBubble.style.borderRadius = '18px';
    messageBubble.style.fontSize = '14px';
    messageBubble.style.lineHeight = '1.4';
    
    // Style based on sender
    if (isStaffReply) {
        messageBubble.style.background = 'white';
        messageBubble.style.color = '#333';
        messageBubble.style.border = '1px solid #e5e7eb';
        messageBubble.style.borderBottomLeftRadius = '4px';
        messageBubble.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    } else {
        messageBubble.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        messageBubble.style.color = 'white';
        messageBubble.style.borderBottomRightRadius = '4px';
    }
    
    // Create timestamp
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date(timestamp).toLocaleTimeString();
    messageTime.style.fontSize = '11px';
    messageTime.style.color = '#999';
    messageTime.style.marginTop = '4px';
    messageTime.style.textAlign = 'center';
    
    // Assemble message
    messageDiv.appendChild(messageBubble);
    messageDiv.appendChild(messageTime);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    console.log('✅ Message added to chat display');
}

/**
 * Load existing messages from database
 * This retrieves all messages for the current session
 */
function loadExistingMessages() {
    if (!chatSessionKey) {
        console.log('❌ No session key available for loading messages');
        return;
    }
    
    console.log('📥 Loading existing messages for session:', chatSessionKey);
    
    fetch(`/chat/session/${chatSessionKey}/messages/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages) {
                console.log(`📨 Loading ${data.messages.length} existing messages`);
                
                // Clear existing messages
                const messagesContainer = document.getElementById('chat-messages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
                
                // Add all messages to display
                data.messages.forEach(msg => {
                    addMessageToChat(msg.message, msg.is_staff_reply, msg.timestamp);
                });
                
                console.log('✅ Existing messages loaded');
            }
        })
        .catch(error => {
            console.error('❌ Error loading existing messages:', error);
        });
}

/**
 * Start message polling as fallback mechanism
 * This checks for new messages every 2 seconds if WebSocket fails
 */
function startMessagePolling() {
    console.log('🔄 Starting message polling...');
    
    // Clear any existing polling
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
    }
    
    // Start new polling
    messagePollingInterval = setInterval(() => {
        checkForNewMessages();
        checkSessionStatus(); // Also check if session is still active
    }, 2000);
}

/**
 * Check for new messages via HTTP
 * This is a fallback mechanism when WebSocket is not available
 */
function checkForNewMessages() {
    if (!chatSessionKey) return;
    
    fetch(`/chat/session/${chatSessionKey}/messages/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages) {
                const messagesContainer = document.getElementById('chat-messages');
                const currentMessageCount = messagesContainer.children.length;
                
                if (data.messages.length > currentMessageCount) {
                    console.log('🔄 New messages detected via polling, reloading...');
                    
                    // Clear and reload all messages
                    messagesContainer.innerHTML = '';
                    data.messages.forEach(msg => {
                        addMessageToChat(msg.message, msg.is_staff_reply, msg.timestamp);
                    });
                }
                
                // Check if session is still active
                if (data.session_info && !data.session_info.is_active) {
                    console.log('🔒 Session has been closed by admin');
                    handleSessionClosed();
                }
            }
        })
        .catch(error => {
            console.error('❌ Error checking for new messages:', error);
        });
}

/**
 * Check session status
 * This checks if the session is still active
 */
function checkSessionStatus() {
    if (!chatSessionKey) return;
    
    fetch(`/chat/session/${chatSessionKey}/status/`)
        .then(response => response.json())
        .then(data => {
            if (!data.is_active) {
                console.log('🔒 Session has been closed by admin');
                handleSessionClosed();
            }
        })
        .catch(error => {
            console.error('❌ Error checking session status:', error);
        });
}

/**
 * Handle session closure
 * This is called when the session has been closed by admin
 */
function handleSessionClosed() {
    console.log('🔒 Handling session closure...');
    
    // Disable chat input and send button
    const messageInput = document.getElementById('chat-message-input');
    const sendBtn = document.getElementById('chat-send-btn');
    
    if (messageInput) {
        messageInput.disabled = true;
        messageInput.placeholder = 'Chat session has been closed by support';
    }
    
    if (sendBtn) {
        sendBtn.disabled = true;
    }
    
    // Show closure message
    addMessageToChat('This chat session has been closed by our support team. Thank you for contacting us!', true, new Date().toISOString());
    
    // Close WebSocket connection
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
        isConnected = false;
    }
    
    // Stop message polling
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
        messagePollingInterval = null;
    }
    
    // Clear session from localStorage
    localStorage.removeItem('chat_session_key');
    localStorage.removeItem('chat_name');
    localStorage.removeItem('chat_email');
    
    console.log('✅ Session closure handled');
}

/**
 * Open chat widget
 */
function openChatWidget() {
    const chatWidget = document.getElementById('chat-widget');
    const chatButton = document.getElementById('chat-button');
    
    if (chatWidget) {
        chatWidget.style.display = 'flex';
        chatWidget.classList.add('show');
    }
    
    if (chatButton) {
        chatButton.style.display = 'none';
    }
    
    // If we have an existing session, show messages and connect
    if (chatSessionKey) {
        console.log('📱 Opening existing session:', chatSessionKey);
        showChatMessages();
        loadExistingMessages();
        connectWebSocket();
        startMessagePolling();
    } else {
        // Focus on name input if pre-chat form is shown
        const nameInput = document.getElementById('user-name');
        if (nameInput && nameInput.offsetParent !== null) {
            nameInput.focus();
        }
    }
}

/**
 * Close chat widget
 */
function closeChatWidget() {
    const chatWidget = document.getElementById('chat-widget');
    const chatButton = document.getElementById('chat-button');
    
    if (chatWidget) {
        chatWidget.style.display = 'none';
    }
    
    if (chatButton) {
        chatButton.style.display = 'flex';
    }
    
    // Close WebSocket connection
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
        isConnected = false;
    }
    
    // Stop message polling
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
        messagePollingInterval = null;
    }
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Debug functions for testing
window.testChat = function() {
    console.log('🧪 Testing chat functionality...');
    console.log('Session key:', chatSessionKey);
    console.log('WebSocket connected:', isConnected);
    console.log('WebSocket ready state:', chatSocket?.readyState);
};

window.testMessageDisplay = function() {
    console.log('🧪 Testing message display...');
    addMessageToChat("Test message from admin", true, new Date().toISOString());
};

window.forceReloadMessages = function() {
    console.log('🔄 Force reloading messages...');
    loadExistingMessages();
};

window.testAdminMessage = function(message = "Test admin message") {
    console.log('🧪 Testing admin message display...');
    addMessageToChat(message, true, new Date().toISOString());
};

window.testSessionStatus = function() {
    console.log('🧪 Testing session status check...');
    checkSessionStatus();
};

window.testSessionClosure = function() {
    console.log('🧪 Testing session closure handling...');
    handleSessionClosed();
};

console.log('💡 Chat widget loaded. Use testChat() to test functionality.');
console.log('💡 Use testMessageDisplay() to test message display.');
console.log('💡 Use forceReloadMessages() to reload messages from server.');
console.log('💡 Use testAdminMessage("your message") to test admin message display.');
console.log('💡 Use testSessionStatus() to check session status.');
console.log('💡 Use testSessionClosure() to test session closure handling.');