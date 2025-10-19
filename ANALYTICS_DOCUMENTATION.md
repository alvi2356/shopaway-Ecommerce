# ShopAway Analytics System Documentation

## Overview

The ShopAway Analytics System provides comprehensive real-time business intelligence and performance tracking for the e-commerce platform. It includes sales analytics, product performance tracking, customer behavior analysis, and interactive dashboards.

## Features

### ✅ **Real-Time Analytics Dashboard**
- **Live Metrics**: Today's sales, orders, products sold, and average order value
- **Growth Tracking**: Day-over-day growth calculations with percentage indicators
- **Interactive Charts**: Sales trends, order status breakdown, payment method distribution
- **Auto-Refresh**: Dashboard updates every 5 minutes automatically

### ✅ **Sales Analytics**
- **Daily Sales Tracking**: Comprehensive daily sales metrics
- **Order Status Monitoring**: Pending, confirmed, shipped, delivered, cancelled orders
- **Payment Method Analysis**: Cash on Delivery vs Online Payment breakdown
- **Customer Segmentation**: New vs returning customer tracking
- **Revenue Analysis**: Total sales, average order value, and growth rates

### ✅ **Product Analytics**
- **Performance Tracking**: Page views, add to cart, purchase counts
- **Conversion Metrics**: View-to-cart, cart-to-purchase, view-to-purchase rates
- **Sales Data**: Units sold and revenue per product
- **Category Analysis**: Top-performing categories and products

### ✅ **Customer Analytics**
- **Behavior Tracking**: Page views, sessions, time on site
- **Purchase History**: Orders count, total spent, average order value
- **Customer Segmentation**: New, regular, VIP, at-risk, inactive customers
- **Activity Monitoring**: Product interactions and engagement metrics

### ✅ **Event Tracking**
- **User Interactions**: Page views, product views, cart actions
- **E-commerce Events**: Checkout starts, purchases, search queries
- **Session Tracking**: User sessions, referrers, device information
- **Custom Events**: Flexible event tracking for business-specific metrics

## Models

### SalesAnalytics
Tracks daily sales performance with comprehensive metrics:
```python
- date: Daily date for analytics
- total_sales: Total revenue for the day
- total_orders: Number of orders placed
- total_products_sold: Total units sold
- average_order_value: Average order value
- new_customers: Number of new customers
- returning_customers: Number of returning customers
- cod_orders/online_orders: Payment method breakdown
- cod_revenue/online_revenue: Revenue by payment method
- pending_orders/confirmed_orders/shipped_orders/delivered_orders/cancelled_orders: Status breakdown
```

### ProductAnalytics
Monitors individual product performance:
```python
- product: Foreign key to Product model
- date: Analytics date
- page_views: Number of product page views
- add_to_cart_count: Add to cart events
- purchase_count: Purchase events
- units_sold: Units sold
- revenue: Revenue generated
- view_to_cart_rate: Conversion rate from view to cart
- cart_to_purchase_rate: Conversion rate from cart to purchase
- view_to_purchase_rate: Overall conversion rate
```

### CustomerAnalytics
Tracks customer behavior and segmentation:
```python
- user: Foreign key to User model
- date: Analytics date
- page_views: Customer page views
- sessions: Number of sessions
- time_on_site: Time spent on site (seconds)
- orders_count: Number of orders placed
- total_spent: Total amount spent
- average_order_value: Average order value
- products_viewed: Products viewed
- products_added_to_cart: Products added to cart
- products_purchased: Products purchased
- segment: Customer segment (new, regular, vip, at_risk, inactive)
```

### AnalyticsEvent
Tracks user interactions and events:
```python
- event_type: Type of event (page_view, product_view, add_to_cart, etc.)
- user: User who triggered the event
- session_id: Session identifier
- page_url: URL where event occurred
- page_title: Page title
- referrer: Referring URL
- user_agent: Browser information
- ip_address: User IP address
- product_id: Product involved (if applicable)
- product_name: Product name
- product_category: Product category
- product_price: Product price
- quantity: Quantity involved
- transaction_id: Transaction ID (for purchases)
- transaction_value: Transaction value
- metadata: Additional event data
```

## API Endpoints

### Analytics Dashboard
- **URL**: `/analytics/`
- **Method**: GET
- **Description**: Main analytics dashboard with real-time data
- **Authentication**: Login required

### Analytics API
- **URL**: `/analytics/api/`
- **Method**: GET
- **Parameters**:
  - `type=overview`: Get overview metrics
  - `type=sales`: Get sales chart data
  - `type=orders`: Get orders chart data
  - `type=products`: Get top products data
  - `type=categories`: Get top categories data
  - `type=payment_methods`: Get payment method breakdown
  - `type=order_status`: Get order status breakdown

### Event Tracking
- **URL**: `/analytics/track/`
- **Method**: POST
- **Description**: Track analytics events
- **Body**: JSON with event data

### Product Analytics
- **URL**: `/analytics/product/<product_id>/`
- **Method**: GET
- **Description**: Product-specific analytics

### Customer Analytics
- **URL**: `/analytics/customers/`
- **Method**: GET
- **Description**: Customer analytics and segmentation

## Admin Integration

### Admin Dashboard
The admin dashboard has been enhanced with real analytics data:
- **Real Metrics**: Shows actual sales, orders, and performance data
- **Growth Indicators**: Displays growth percentages vs previous day
- **Interactive Charts**: Sales trends and payment method breakdown
- **Recent Activity**: Latest orders and system alerts
- **Quick Actions**: Direct links to analytics and management pages

### Admin Models
All analytics models are registered with Django admin:
- **SalesAnalytics**: Daily sales performance management
- **ProductAnalytics**: Product performance tracking
- **CustomerAnalytics**: Customer behavior analysis
- **AnalyticsEvent**: Event tracking and monitoring
- **AnalyticsDashboard**: Dashboard configuration
- **AnalyticsWidget**: Widget configuration

## Management Commands

### Populate Analytics Data
```bash
python manage.py populate_analytics --days 30 --clear
```
- Generates sample analytics data for testing
- `--days`: Number of days to generate data for
- `--clear`: Clear existing data before populating

### Generate Sample Data
```bash
python manage.py generate_sample_data
```
- Creates sample analytics data for the last 7 days
- Useful for testing and demonstration

## Usage Examples

### Tracking Events
```javascript
// Track a page view
fetch('/analytics/track/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        event_type: 'page_view',
        page_url: window.location.href,
        page_title: document.title
    })
});

// Track a product view
fetch('/analytics/track/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        event_type: 'product_view',
        product_id: '123',
        product_name: 'Sample Product',
        product_category: 'Electronics',
        product_price: 99.99
    })
});
```

### Getting Analytics Data
```javascript
// Get overview data
fetch('/analytics/api/?type=overview')
    .then(response => response.json())
    .then(data => {
        console.log('Today\'s sales:', data.today.sales);
        console.log('Growth:', data.growth.sales_growth + '%');
    });

// Get sales chart data
fetch('/analytics/api/?type=sales')
    .then(response => response.json())
    .then(data => {
        // Use data for Chart.js
        updateSalesChart(data);
    });
```

## Performance Considerations

### Caching
- API responses are cached for 5 minutes using `@cache_page(60 * 5)`
- Database queries are optimized with `select_related()` and `prefetch_related()`
- Indexes are created on frequently queried fields

### Database Optimization
- Proper indexing on date fields and foreign keys
- Efficient aggregation queries using Django ORM
- Minimal database hits through query optimization

### Real-time Updates
- Dashboard auto-refreshes every 5 minutes
- Manual refresh button for immediate updates
- WebSocket integration ready for real-time updates

## Security

### Authentication
- All analytics endpoints require authentication
- Admin views require staff permissions
- API endpoints validate user permissions

### Data Privacy
- IP addresses are stored for analytics purposes
- User data is anonymized where possible
- GDPR compliance considerations included

## Future Enhancements

### Planned Features
- **Real-time WebSocket Updates**: Live dashboard updates
- **Advanced Segmentation**: More sophisticated customer segmentation
- **Predictive Analytics**: Sales forecasting and trend prediction
- **Custom Reports**: User-configurable report generation
- **Export Functionality**: CSV/PDF export of analytics data
- **Mobile App Integration**: Analytics for mobile applications
- **A/B Testing**: Built-in A/B testing framework
- **Heatmaps**: User behavior heatmaps
- **Funnel Analysis**: Conversion funnel tracking

### Integration Opportunities
- **Google Analytics**: Integration with Google Analytics
- **Facebook Pixel**: Social media tracking
- **Email Marketing**: Integration with email platforms
- **CRM Systems**: Customer relationship management integration
- **Business Intelligence**: Advanced BI tool integration

## Troubleshooting

### Common Issues

1. **Database Locked Error**
   - Solution: Stop the development server before running management commands
   - Alternative: Use `--clear` flag to avoid conflicts

2. **No Data Showing**
   - Solution: Run `python manage.py generate_sample_data` to create test data
   - Check if analytics models are properly migrated

3. **Charts Not Loading**
   - Solution: Ensure Chart.js is loaded and JavaScript is enabled
   - Check browser console for JavaScript errors

4. **API Timeout**
   - Solution: Check database performance and query optimization
   - Consider increasing cache duration for heavy queries

### Debug Mode
Enable debug mode in settings to see detailed error messages:
```python
DEBUG = True
```

## Support

For technical support or feature requests, please refer to the project documentation or contact the development team.

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
