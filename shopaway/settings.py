import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
# Load env from project root explicitly
load_dotenv(dotenv_path=BASE_DIR / '.env')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    'sylvester-flutier-quincuncially.ngrok-free.dev',
    '.vercel.app',  # For Vercel deployment
    '.herokuapp.com',  # For Heroku deployment
    '.railway.app',  # For Railway deployment
    '.render.com',  # For Render deployment
    '.pythonanywhere.com',  # For PythonAnywhere
    '*',  # Allow all hosts for development (remove in production)
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework','crispy_forms','django_filters',
    'channels',
    'accounts','products','orders','inventory','chat','analytics',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static optimization
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
ROOT_URLCONF = 'shopaway.urls'
TEMPLATES = [
    { 'BACKEND': 'django.template.backends.django.DjangoTemplates',
       'DIRS': [BASE_DIR / 'templates'],
       'APP_DIRS': True,
       'OPTIONS': { 'context_processors': [
           'django.template.context_processors.debug',
           'django.template.context_processors.request',
           'django.contrib.auth.context_processors.auth',
           'django.contrib.messages.context_processors.messages',
           'products.context_processors.cart_context',
        ]},
    }
]
WSGI_APPLICATION = 'shopaway.wsgi.application'
ASGI_APPLICATION = 'routing.application'
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3','NAME': BASE_DIR / 'db.sqlite3' } }
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# CSRF Settings for Production
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.herokuapp.com',
    'https://*.railway.app',
    'https://*.render.com',
    'https://*.pythonanywhere.com',
    'https://sylvester-flutier-quincuncially.ngrok-free.dev',
]

# CSRF Cookie Settings
CSRF_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Session Settings
SESSION_COOKIE_SECURE = not DEBUG  # Use secure cookies in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Additional CSRF Settings
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_USE_SESSIONS = False

# Crispy Forms configuration
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Jazzmin branding for an eye-catching admin with modern theme
JAZZMIN_SETTINGS = {
    # General Settings
    "site_title": "ShopAway Admin",
    "site_header": "ShopAway",
    "site_brand": "ShopAway",
    "welcome_sign": "Welcome to ShopAway Admin Dashboard",
    "copyright": "ShopAway E-commerce Platform",
    "search_model": ["auth.User", "products.Product", "orders.Order"],
    
    # UI Theme Configuration
    "theme": "darkly",  # Modern dark theme
    "dark_mode_theme": "darkly",
    "show_ui_builder": True,
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": ["blog"],  # Hide blog app from admin
    "hide_models": [],
    
    # Custom CSS and JS
    "custom_css": "admin/css/custom-admin.css",
    "custom_js": "admin/js/custom-admin.js",
    
    # Color Scheme - Modern Purple/Blue Gradient
    "brand_colors": {
        "primary": "#6366f1",  # Indigo
        "secondary": "#8b5cf6",  # Purple
        "accent": "#06b6d4",  # Cyan
        "success": "#10b981",  # Emerald
        "warning": "#f59e0b",  # Amber
        "danger": "#ef4444",  # Red
        "info": "#3b82f6",  # Blue
        "light": "#f8fafc",  # Slate 50
        "dark": "#1e293b",  # Slate 800
    },
    
    # Logo and Branding
    "logo": None,  # Will use text logo
    "logo_classes": "img-circle elevation-3",
    "site_logo": None,
    "site_logo_classes": "img-circle elevation-3",
    
    # Top Menu Links
    "topmenu_links": [
        {"name": "🏠 Home", "url": "/", "permissions": ["auth.view_user"]},
        {"name": "📊 Analytics", "url": "/analytics/", "permissions": ["auth.view_user"]},
        {"app": "products"},
        {"app": "orders"},
        {"name": "💬 Live Chat", "url": "/chat/admin/", "permissions": ["auth.view_user"]},
        {"name": "📦 Inventory", "url": "/admin/inventory/", "permissions": ["auth.view_user"]},
    ],
    
    # Sidebar Configuration
    "order_with_respect_to": ["auth", "products", "orders", "inventory", "analytics", "chat"],
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
    
    # Icons with modern FontAwesome icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "products": "fas fa-boxes",
        "products.product": "fas fa-box",
        "products.category": "fas fa-tags",
        "orders": "fas fa-shopping-cart",
        "orders.order": "fas fa-receipt",
        "orders.orderitem": "fas fa-list",
        "inventory": "fas fa-warehouse",
        "inventory.stocktransaction": "fas fa-exchange-alt",
        "analytics": "fas fa-chart-line",
        "analytics.analyticsdashboard": "fas fa-tachometer-alt",
        "chat": "fas fa-comments",
        "chat.chatmessage": "fas fa-comment",
    },
    
    # Custom Links
    "custom_links": {
        "products": [{
            "name": "📈 Product Analytics",
            "url": "/analytics/products/",
            "icon": "fas fa-chart-bar",
            "permissions": ["auth.view_user"]
        }],
        "orders": [{
            "name": "📊 Order Reports",
            "url": "/analytics/orders/",
            "icon": "fas fa-chart-pie",
            "permissions": ["auth.view_user"]
        }],
    },
    
    # UI Builder Settings
    "show_ui_builder": True,
    "ui_builder_on_top": True,
    
    # Language and Localization
    "language_chooser": False,  # Disabled to avoid URL configuration issues
    "default_ui_theme": "darkly",
    
    # Performance
    "related_modal_active": True,
    "related_modal_backdrop": True,
}
# Email & SMS placeholders
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST','')
EMAIL_PORT = int(os.getenv('EMAIL_PORT','587') or 587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','')
# Simple cache for speed optimization (local memory cache — swap for redis in prod)
CACHES = { 'default': { 'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' } }

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Pathao Courier configuration (Sandbox defaults). Keep secrets in environment.
def _env(name: str, default: str = ""):
    val = os.getenv(name, default)
    if isinstance(val, str):
        # Trim whitespace and any surrounding single/double quotes
        val = val.strip().strip('"').strip("'")
    return val

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return float(default)

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return int(default)

PATHAO = {
    "BASE_URL": _env("PATHAO_BASE_URL", "https://courier-api-sandbox.pathao.com"),
    "CLIENT_ID": _env("PATHAO_CLIENT_ID", ""),
    "CLIENT_SECRET": _env("PATHAO_CLIENT_SECRET", ""),
    "USERNAME": _env("PATHAO_USERNAME", ""),
    "PASSWORD": _env("PATHAO_PASSWORD", ""),
    # Optional overrides
    "ISSUE_TOKEN_PATH": _env("PATHAO_ISSUE_TOKEN_PATH", "/aladdin/api/v1/issue-token"),
    "CREATE_ORDER_PATH": _env("PATHAO_CREATE_ORDER_PATH", "/aladdin/api/v1/orders"),
    "ORDER_STATUS_PATH": _env("PATHAO_ORDER_STATUS_PATH", "/aladdin/api/v1/orders/{order_id}"),
    # Networking
    "CONNECT_TIMEOUT": _env_float("PATHAO_CONNECT_TIMEOUT", 5.0),
    "READ_TIMEOUT": _env_float("PATHAO_READ_TIMEOUT", 20.0),
    "RETRIES": _env_int("PATHAO_RETRIES", 2),
    # Token request configuration
    "GRANT_TYPE": _env("PATHAO_GRANT_TYPE", "password"),  # or "client_credentials"
    "USERNAME_FIELD": _env("PATHAO_USERNAME_FIELD", "username"),  # some tenants use "email"
    "SCOPE": _env("PATHAO_SCOPE", ""),
    # Webhook shared secret token for validation
    "WEBHOOK_TOKEN": _env("PATHAO_WEBHOOK_TOKEN", ""),
}

# Steadfast Courier configuration
STEADFAST = {
    "BASE_URL": _env("STEADFAST_BASE_URL", "https://portal.steadfast.com.bd/api/v1"),
    "API_KEY": _env("STEADFAST_API_KEY", ""),
    "SECRET_KEY": _env("STEADFAST_SECRET_KEY", ""),
    "USE_MOCK": (_env("STEADFAST_USE_MOCK", "True") == "True"),
    # Endpoint overrides
    "CREATE_ORDER_PATH": _env("STEADFAST_CREATE_ORDER_PATH", "/create_order"),
    "STATUS_BY_CID_PATH": _env("STEADFAST_STATUS_BY_CID_PATH", "/status_by_cid/{consignment_id}"),
    # Networking
    "CONNECT_TIMEOUT": _env_float("STEADFAST_CONNECT_TIMEOUT", 5.0),
    "READ_TIMEOUT": _env_float("STEADFAST_READ_TIMEOUT", 20.0),
    "RETRIES": _env_int("STEADFAST_RETRIES", 2),
    # Defaults to satisfy common required fields for create_order
    "DEFAULTS": {
        "recipient_city": _env("STEADFAST_DEFAULT_CITY", "Dhaka"),
        "recipient_area": _env("STEADFAST_DEFAULT_AREA", "Dhaka"),
        "delivery_type": _env("STEADFAST_DEFAULT_DELIVERY", "standard"),
        "weight": _env_float("STEADFAST_DEFAULT_WEIGHT", 1.0),
        "payment_method": _env("STEADFAST_DEFAULT_PAYMENT_METHOD", "COD"),
    },
}
