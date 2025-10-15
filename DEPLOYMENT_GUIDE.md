# ShopAway Deployment Guide

## CSRF Error Fix

If you're getting "Forbidden (403) CSRF verification failed" when accessing the admin panel on your host, follow these steps:

### 1. Environment Variables

Create a `.env` file in your project root with these variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# Add your specific host domain
ALLOWED_HOST=your-domain.com
```

### 2. Update ALLOWED_HOSTS

In `shopaway/settings.py`, add your specific domain to ALLOWED_HOSTS:

```python
ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    'your-domain.com',  # Add your actual domain here
    'your-app.herokuapp.com',  # If using Heroku
    'your-app.vercel.app',  # If using Vercel
    # ... other hosts
]
```

### 3. Update CSRF_TRUSTED_ORIGINS

Add your domain to CSRF_TRUSTED_ORIGINS:

```python
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://your-app.herokuapp.com',
    'https://your-app.vercel.app',
    # ... other origins
]
```

### 4. Generate New Secret Key

Run this command to generate a new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Clear Browser Cache

Clear your browser cache and cookies for the site, then try accessing the admin panel again.

### 6. Check HTTPS

Make sure you're accessing the admin panel via HTTPS in production.

### 7. Alternative: Temporary CSRF Disable (NOT RECOMMENDED FOR PRODUCTION)

If you need immediate access, you can temporarily disable CSRF for admin (remove after fixing):

```python
# In settings.py - TEMPORARY FIX ONLY
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
```

## Common Hosting Platforms

### Heroku
- Add your Heroku domain to ALLOWED_HOSTS
- Set environment variables in Heroku dashboard
- Use `heroku config:set DJANGO_SECRET_KEY=your-key`

### Vercel
- Add your Vercel domain to ALLOWED_HOSTS
- Set environment variables in Vercel dashboard
- Update vercel.json if needed

### Railway
- Add your Railway domain to ALLOWED_HOSTS
- Set environment variables in Railway dashboard

### PythonAnywhere
- Add your PythonAnywhere domain to ALLOWED_HOSTS
- Set environment variables in PythonAnywhere dashboard

## Testing

After making changes:
1. Restart your server
2. Clear browser cache
3. Try accessing admin panel again
4. Check server logs for any remaining errors
