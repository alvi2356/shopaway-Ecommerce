import hashlib
import json
import requests
from django.conf import settings
from django.urls import reverse
from urllib.parse import urljoin


class SSLCommerzClient:
    """SSL Commerz payment gateway integration."""
    
    def __init__(self):
        self.store_id = "shopa68e2679c82422"
        self.store_password = "shopa68e2679c82422@ssl"
        # Use sandbox for testing
        self.base_url = "https://sandbox.sslcommerz.com"
    
    def create_payment_session(self, order, request):
        """Create a payment session with SSL Commerz."""
        
        # Calculate total amount
        total_amount = float(order.total)
        
        # Create success and fail URLs
        success_url = request.build_absolute_uri(
            reverse('orders:payment_success', kwargs={'order_id': order.id})
        )
        fail_url = request.build_absolute_uri(
            reverse('orders:payment_fail', kwargs={'order_id': order.id})
        )
        cancel_url = request.build_absolute_uri(
            reverse('orders:payment_cancel', kwargs={'order_id': order.id})
        )
        
        # Prepare payment data - enhanced for SSL Commerz
        payment_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_password,
            'total_amount': total_amount,
            'currency': 'BDT',
            'tran_id': f"ORDER_{order.id}_{order.created_at.strftime('%Y%m%d%H%M%S')}",
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'emi_option': 0,
            'cus_name': order.name,
            'cus_email': getattr(order, 'email', ''),
            'cus_add1': order.address,
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_phone': order.phone,
            'shipping_method': 'NO',
            'product_name': f"Order #{order.id}",
            'product_category': 'General',
            'product_profile': 'general',
            'value_a': order.id,  # Store order ID for reference
            'value_b': order.payment_method,  # Store payment method
            'value_c': 'ShopAway',  # Store name
            'value_d': 'Online Store',  # Store type
        }
        
        return payment_data
    
    def initiate_payment(self, payment_data):
        """Initiate payment with SSL Commerz."""
        try:
            # Debug: Print payment data
            print(f"SSL Commerz Payment Data: {payment_data}")
            
            # SSL Commerz uses v3 API endpoint
            response = requests.post(
                f"{self.base_url}/gwprocess/v3/api.php",
                data=payment_data,
                timeout=30
            )
            
            print(f"SSL Commerz Response Status: {response.status_code}")
            print(f"SSL Commerz Response Content: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    # Parse JSON response
                    json_response = response.json()
                    print(f"SSL Commerz JSON Response: {json_response}")
                    
                    if json_response.get('status') == 'SUCCESS':
                        redirect_url = json_response.get('redirectGatewayURL')
                        if redirect_url:
                            return {
                                'status': 'success',
                                'redirect_url': redirect_url
                            }
                        else:
                            return {
                                'status': 'error',
                                'message': 'No redirect URL received from payment gateway'
                            }
                    else:
                        failed_reason = json_response.get('failedreason', 'Payment initialization failed')
                        return {
                            'status': 'error',
                            'message': failed_reason
                        }
                        
                except json.JSONDecodeError:
                    # If not JSON, check for redirect URL in text
                    if 'redirectGatewayURL' in response.text:
                        import re
                        url_match = re.search(r'https://[^\s<>"]+', response.text)
                        if url_match:
                            return {
                                'status': 'success',
                                'redirect_url': url_match.group()
                            }
                    
                    return {
                        'status': 'error',
                        'message': f'Invalid response format from payment gateway. Response: {response.text[:200]}'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP Error: {response.status_code} - {response.text[:200]}'
                }
                
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': f'Request failed: {str(e)}'
            }
    
    def verify_payment(self, request):
        """Verify payment response from SSL Commerz."""
        try:
            # Get payment response data
            val_id = request.GET.get('val_id')
            amount = request.GET.get('amount')
            currency = request.GET.get('currency')
            tran_id = request.GET.get('tran_id')
            
            if not all([val_id, amount, currency, tran_id]):
                return {
                    'status': 'error',
                    'message': 'Missing payment parameters'
                }
            
            # Verify payment with SSL Commerz
            verify_data = {
                'store_id': self.store_id,
                'store_passwd': self.store_password,
                'val_id': val_id,
                'format': 'json'
            }
            
            response = requests.post(
                f"{self.base_url}/validator/api/validationserverAPI.php",
                data=verify_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'data': result
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Verification failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Verification error: {str(e)}'
            }
