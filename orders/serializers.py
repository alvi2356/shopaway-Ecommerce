"""
Django REST Framework serializers for Pathao integration
"""
from rest_framework import serializers
from .models import Order, CourierLog


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'name', 'phone', 'address', 'total', 'status',
            'created_at', 'fraud_flag', 'pathao_order_id',
            'pathao_status', 'pathao_consignment_id', 'pathao_tracking_code',
            'items'
        ]
        read_only_fields = ['id', 'created_at']


class CourierLogSerializer(serializers.ModelSerializer):
    """Serializer for CourierLog model"""
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    
    class Meta:
        model = CourierLog
        fields = [
            'id', 'order_id', 'event_type', 'request_data', 'response_data',
            'status_code', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']




class PathaoOrderCreateSerializer(serializers.Serializer):
    """Serializer for creating Pathao order"""
    order_id = serializers.IntegerField()
    environment = serializers.ChoiceField(choices=['sandbox', 'production'], default='sandbox')
    
    def validate_order_id(self, value):
        """Validate order exists and is eligible for Pathao"""
        try:
            order = Order.objects.get(id=value)
            if order.fraud_flag:
                raise serializers.ValidationError("Order is flagged for fraud and cannot be sent to Pathao")
            if order.pathao_order_id:
                raise serializers.ValidationError("Order already has Pathao order ID")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")


class PathaoStatusRefreshSerializer(serializers.Serializer):
    """Serializer for refreshing Pathao status"""
    order_id = serializers.IntegerField()
    environment = serializers.ChoiceField(choices=['sandbox', 'production'], default='sandbox')
    
    def validate_order_id(self, value):
        """Validate order exists and has Pathao order ID"""
        try:
            order = Order.objects.get(id=value)
            if not order.pathao_order_id:
                raise serializers.ValidationError("Order does not have Pathao order ID")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")


class PathaoWebhookSerializer(serializers.Serializer):
    """Serializer for Pathao webhook payload"""
    order_id = serializers.CharField()
    status = serializers.CharField()
    consignment_id = serializers.CharField(required=False)
    tracking_code = serializers.CharField(required=False)
    security_key = serializers.CharField(required=False)
    
    def validate_security_key(self, value):
        """Validate webhook security key"""
        from django.conf import settings
        expected_key = getattr(settings, 'PATHAO_WEBHOOK_SECURITY_KEY', '')
        if expected_key and value != expected_key:
            raise serializers.ValidationError("Invalid security key")
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order listing"""
    pathao_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'name', 'phone', 'total', 'status', 'created_at',
            'pathao_status', 'pathao_status_display', 'pathao_order_id'
        ]
    
    def get_pathao_status_display(self, obj):
        """Get human-readable Pathao status"""
        if not obj.pathao_status:
            return "Not sent to Pathao"
        return obj.pathao_status.replace('_', ' ').title()


class OrderDetailSerializer(OrderSerializer):
    """Detailed serializer for order with additional information"""
    courier_logs = CourierLogSerializer(source='courier_logs', many=True, read_only=True)
    can_send_to_pathao = serializers.SerializerMethodField()
    can_refresh_status = serializers.SerializerMethodField()
    
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            'courier_logs', 'can_send_to_pathao', 'can_refresh_status'
        ]
    
    def get_can_send_to_pathao(self, obj):
        """Check if order can be sent to Pathao"""
        return (
            not obj.fraud_flag and 
            not obj.pathao_order_id
        )
    
    def get_can_refresh_status(self, obj):
        """Check if order status can be refreshed"""
        return bool(obj.pathao_order_id)


class PathaoOrderResponseSerializer(serializers.Serializer):
    """Serializer for Pathao order creation response"""
    message = serializers.CharField()
    order_id = serializers.IntegerField()
    pathao_order_id = serializers.CharField(required=False)
    pathao_consignment_id = serializers.CharField(required=False)
    pathao_tracking_code = serializers.CharField(required=False)
    pathao_response = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    error = serializers.CharField()
    details = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
