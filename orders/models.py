from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    ORDER_STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.TextField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=ORDER_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=128, blank=True, null=True, unique=True)
    double_entry_hash = models.CharField(max_length=128, blank=True, null=True)

    # Pathao courier integration fields
    pathao_order_id = models.CharField(
        max_length=64, blank=True, null=True, db_index=True, help_text="Pathao courier order ID"
    )
    pathao_status = models.CharField(
        max_length=64, blank=True, null=True, help_text="Latest status from Pathao"
    )
    pathao_response = models.JSONField(
        blank=True, null=True, help_text="Raw latest response from Pathao API"
    )
    pathao_invoice_url = models.CharField(
        max_length=255, blank=True, null=True, help_text="Pathao invoice URL or reference"
    )

    # Fraud check
    is_flagged_fraud = models.BooleanField(default=False)
    fraud_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment fields
    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_gateway_response = models.JSONField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def already_sent_to_courier(self) -> bool:
        return bool(self.pathao_order_id)

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product} x{self.qty}"


class CourierLog(models.Model):
    """Audit trail for courier interactions (webhooks, API calls, etc)."""

    ACTIONS = [
        ("create", "Create Order"),
        ("status", "Refresh Status"),
        ("invoice", "Generate Invoice"),
        ("webhook", "Webhook"),
        ("error", "Error"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="courier_logs", null=True, blank=True
    )
    action = models.CharField(max_length=32, choices=ACTIONS)
    raw_payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"CourierLog(order={self.order_id}, action={self.action}, at={self.created_at:%Y-%m-%d %H:%M})"
