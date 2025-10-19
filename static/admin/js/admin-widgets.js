// ShopAway Admin Widgets - Enhanced Features

class AdminWidgets {
    constructor() {
        this.init();
    }

    init() {
        this.createSystemStatusWidget();
        this.createNotificationCenter();
        this.initializeKeyboardShortcuts();
    }


    // System Status Widget
    createSystemStatusWidget() {
        const statusWidget = document.createElement('div');
        statusWidget.className = 'system-status-widget';
        statusWidget.innerHTML = `
            <div class="status-header">
                <h6><i class="fas fa-server"></i> System Status</h6>
            </div>
            <div class="status-items">
                <div class="status-item">
                    <span class="status-dot online"></span>
                    <span>Database</span>
                </div>
                <div class="status-item">
                    <span class="status-dot online"></span>
                    <span>API</span>
                </div>
                <div class="status-item">
                    <span class="status-dot warning"></span>
                    <span>Cache</span>
                </div>
                <div class="status-item">
                    <span class="status-dot online"></span>
                    <span>Storage</span>
                </div>
            </div>
        `;
        
        statusWidget.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            min-width: 180px;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .status-header h6 {
                margin: 0 0 10px 0;
                color: #6366f1;
                font-weight: 600;
            }
            .status-item {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 14px;
            }
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 10px;
            }
            .status-dot.online { background: #10b981; }
            .status-dot.warning { background: #f59e0b; }
            .status-dot.offline { background: #ef4444; }
        `;
        document.head.appendChild(style);
        document.body.appendChild(statusWidget);
    }



    // Notification Center
    createNotificationCenter() {
        const notificationCenter = document.createElement('div');
        notificationCenter.className = 'notification-center';
        notificationCenter.innerHTML = `
            <div class="notification-header">
                <h6><i class="fas fa-bell"></i> Notifications</h6>
                <button class="clear-all-btn">Clear All</button>
            </div>
            <div class="notification-list">
                <div class="notification-item unread">
                    <div class="notification-icon">
                        <i class="fas fa-exclamation-triangle text-warning"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">Low Stock Alert</div>
                        <div class="notification-message">Product "Wireless Headphones" is running low</div>
                        <div class="notification-time">5 minutes ago</div>
                    </div>
                </div>
                <div class="notification-item">
                    <div class="notification-icon">
                        <i class="fas fa-shopping-cart text-success"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">New Order</div>
                        <div class="notification-message">Order #1235 has been placed</div>
                        <div class="notification-time">15 minutes ago</div>
                    </div>
                </div>
            </div>
        `;
        
        notificationCenter.style.cssText = `
            position: fixed;
            top: 300px;
            right: 20px;
            background: white;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            min-width: 300px;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .notification-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .notification-header h6 {
                margin: 0;
                color: #6366f1;
                font-weight: 600;
            }
            .clear-all-btn {
                background: none;
                border: none;
                color: #64748b;
                font-size: 12px;
                cursor: pointer;
            }
            .notification-item {
                display: flex;
                align-items: flex-start;
                margin-bottom: 12px;
                padding: 12px;
                border-radius: 10px;
                border-left: 3px solid transparent;
                transition: all 0.3s ease;
            }
            .notification-item.unread {
                background: #fef3c7;
                border-left-color: #f59e0b;
            }
            .notification-item:hover {
                background: #f8fafc;
            }
            .notification-icon {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: #f1f5f9;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                flex-shrink: 0;
            }
            .notification-content {
                flex: 1;
            }
            .notification-title {
                font-size: 14px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 4px;
            }
            .notification-message {
                font-size: 13px;
                color: #64748b;
                margin-bottom: 4px;
            }
            .notification-time {
                font-size: 11px;
                color: #94a3b8;
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(notificationCenter);

        // Add notification bell to navbar
        const notificationBell = document.createElement('button');
        notificationBell.className = 'notification-bell';
        notificationBell.innerHTML = '<i class="fas fa-bell"></i>';
        notificationBell.style.cssText = `
            position: fixed;
            top: 20px;
            right: 80px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            transition: all 0.3s ease;
            z-index: 9999;
        `;
        
        notificationBell.addEventListener('click', () => {
            notificationCenter.style.display = notificationCenter.style.display === 'none' ? 'block' : 'none';
        });
        
        document.body.appendChild(notificationBell);
    }

    // Keyboard Shortcuts
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + N for new notification
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                this.showTestNotification();
            }
            
            // Ctrl/Cmd + Shift + S for system status
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                this.toggleSystemStatus();
            }
        });
    }

    showTestNotification() {
        const notification = document.createElement('div');
        notification.className = 'test-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-info-circle"></i>
                <span>Test notification from keyboard shortcut!</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    toggleSystemStatus() {
        const statusWidget = document.querySelector('.system-status-widget');
        if (statusWidget) {
            statusWidget.style.display = statusWidget.style.display === 'none' ? 'block' : 'none';
        }
    }
}

// Initialize widgets when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AdminWidgets();
});

// Export for global use
window.AdminWidgets = AdminWidgets;
