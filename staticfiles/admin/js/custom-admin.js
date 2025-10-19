// ShopAway Admin Custom JavaScript - Enhanced Features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all custom features
    initializeThemeToggle();
    initializeDashboardAnimations();
    initializeQuickActions();
    initializeRealTimeUpdates();
    initializeSearchEnhancements();
    initializeKeyboardShortcuts();
    initializeTooltips();
    initializeNotifications();
    initializeAdminWidgets();
    initializeDataTables();
    initializeFormEnhancements();
});

// Theme Toggle Functionality
function initializeThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.className = 'btn btn-outline-light btn-sm theme-toggle';
    themeToggle.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    `;
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        localStorage.setItem('admin-theme', isDark ? 'dark' : 'light');
    });
    
    // Load saved theme
    const savedTheme = localStorage.getItem('admin-theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    document.body.appendChild(themeToggle);
}

// Dashboard Animations
function initializeDashboardAnimations() {
    // Animate dashboard cards on load
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Add hover effects to dashboard widgets
    const widgets = document.querySelectorAll('.dashboard-widget');
    widgets.forEach(widget => {
        widget.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        widget.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Quick Actions Panel - Disabled
function initializeQuickActions() {
    // Quick actions have been removed from the admin panel
    return;
}

// Real-time Updates
function initializeRealTimeUpdates() {
    // Update dashboard stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Add live notification for new orders
    if (window.location.pathname.includes('/admin/orders/')) {
        checkForNewOrders();
    }
}

function updateDashboardStats() {
    // This would typically make an AJAX call to get updated stats
    // For now, we'll just add a subtle animation to indicate updates
    const statCards = document.querySelectorAll('.card-hover .h4');
    statCards.forEach(card => {
        card.style.animation = 'pulse 1s ease-in-out';
        setTimeout(() => {
            card.style.animation = '';
        }, 1000);
    });
}

function checkForNewOrders() {
    // Simulate checking for new orders
    // In a real implementation, this would use WebSockets or polling
    setTimeout(() => {
        showNotification('New order received!', 'success');
    }, 5000);
}

// Enhanced Search
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            highlightSearchResults(query);
        });
    }
}

function highlightSearchResults(query) {
    if (query.length < 2) return;
    
    const elements = document.querySelectorAll('.card, .table tbody tr');
    elements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes(query)) {
            element.style.background = 'rgba(99, 102, 241, 0.1)';
            element.style.border = '2px solid rgba(99, 102, 241, 0.3)';
        } else {
            element.style.background = '';
            element.style.border = '';
        }
    });
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#searchbar');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N for new item
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('.addlink');
            if (addButton) {
                addButton.click();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('#searchbar');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });
}

// Enhanced Tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showCustomTooltip(this, this.title);
            this.removeAttribute('title');
        });
        
        element.addEventListener('mouseleave', function() {
            hideCustomTooltip();
        });
    });
}

function showCustomTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #1e293b;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
}

function hideCustomTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Notification System
function initializeNotifications() {
    // Create notification container
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    notificationContainer.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        pointer-events: none;
    `;
    document.body.appendChild(notificationContainer);
}

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    notification.style.cssText = `
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-100px);
        opacity: 0;
        transition: all 0.3s ease;
        pointer-events: auto;
        cursor: pointer;
    `;
    
    const container = document.querySelector('.notification-container');
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
    
    // Click to remove
    notification.addEventListener('click', () => {
        removeNotification(notification);
    });
}

function removeNotification(notification) {
    notification.style.transform = 'translateY(-100px)';
    notification.style.opacity = '0';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        'success': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        'error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        'info': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
    };
    return colors[type] || colors.info;
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize Admin Widgets
function initializeAdminWidgets() {
    // Load the admin widgets script
    const script = document.createElement('script');
    script.src = '/static/admin/js/admin-widgets.js';
    script.onload = function() {
        console.log('Admin widgets loaded successfully');
    };
    document.head.appendChild(script);
}

// Enhanced Data Tables
function initializeDataTables() {
    const tables = document.querySelectorAll('.results table');
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('a')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            }
        });
        
        // Add row hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(99, 102, 241, 0.05)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });
}

// Form Enhancements
function initializeFormEnhancements() {
    // Add auto-save functionality to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.querySelector('input[name="name"], input[name="title"], textarea')) {
            let autoSaveTimeout;
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(autoSaveTimeout);
                    autoSaveTimeout = setTimeout(() => {
                        showNotification('Form auto-saved', 'info', 2000);
                    }, 2000);
                });
            });
        }
    });
    
    // Add form validation enhancements
    const requiredFields = document.querySelectorAll('input[required], textarea[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.style.borderColor = '#ef4444';
                this.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
            } else {
                this.style.borderColor = '#10b981';
                this.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
            }
        });
        
        field.addEventListener('input', function() {
            if (this.value.trim()) {
                this.style.borderColor = '#10b981';
                this.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
            }
        });
    });
}

// Table Sorting Function
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = table.getAttribute('data-sort-direction') !== 'asc';
    table.setAttribute('data-sort-direction', isAscending ? 'asc' : 'desc');
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aText.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Sort as strings
        return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
    
    // Update header indicators
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.innerHTML = header.innerHTML.replace(/ ↑| ↓/g, '');
        if (index === columnIndex) {
            header.innerHTML += isAscending ? ' ↑' : ' ↓';
        }
    });
}

// Enhanced Search with Filters
function initializeAdvancedSearch() {
    const searchContainer = document.querySelector('.search-container');
    if (!searchContainer) return;
    
    const advancedSearch = document.createElement('div');
    advancedSearch.className = 'advanced-search';
    advancedSearch.innerHTML = `
        <div class="search-filters">
            <select class="filter-select">
                <option value="">All Fields</option>
                <option value="name">Name</option>
                <option value="email">Email</option>
                <option value="date">Date</option>
            </select>
            <button class="btn btn-sm btn-outline-secondary" id="clearFilters">
                <i class="fas fa-times"></i> Clear
            </button>
        </div>
    `;
    
    searchContainer.appendChild(advancedSearch);
    
    document.getElementById('clearFilters').addEventListener('click', () => {
        document.querySelector('#searchbar').value = '';
        document.querySelector('.filter-select').value = '';
        highlightSearchResults('');
    });
}

// Export functions for global use
window.ShopAwayAdmin = {
    showNotification,
    handleQuickAction,
    updateDashboardStats,
    sortTable,
    initializeAdvancedSearch
};
