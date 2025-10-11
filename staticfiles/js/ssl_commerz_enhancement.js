// SSL Commerz Payment Gateway Enhancement Script
(function() {
    'use strict';
    
    // Wait for page to load
    document.addEventListener('DOMContentLoaded', function() {
        enhanceSSLCommerzPage();
    });
    
    function enhanceSSLCommerzPage() {
        // Add custom CSS
        addCustomStyles();
        
        // Enhance form validation
        enhanceFormValidation();
        
        // Add helpful tooltips
        addTooltips();
        
        // Improve button styling
        enhanceButtons();
        
        // Add loading states
        addLoadingStates();
    }
    
    function addCustomStyles() {
        // Inject our custom CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/ssl_commerz.css';
        document.head.appendChild(link);
    }
    
    function enhanceFormValidation() {
        const cardNumberInput = document.querySelector('input[name="card_number"], input[type="text"]');
        const cvvInput = document.querySelector('input[name="cvv"], input[type="text"]');
        const cardholderInput = document.querySelector('input[name="cardholder_name"], input[type="text"]');
        
        if (cardNumberInput) {
            // Format card number
            cardNumberInput.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
                let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
                e.target.value = formattedValue;
            });
            
            // Add card type detection
            cardNumberInput.addEventListener('input', function(e) {
                const value = e.target.value.replace(/\s/g, '');
                const cardType = detectCardType(value);
                if (cardType) {
                    e.target.setAttribute('data-card-type', cardType);
                }
            });
        }
        
        if (cvvInput) {
            // Limit CVV to 3-4 digits
            cvvInput.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/[^0-9]/gi, '').substring(0, 4);
            });
        }
    }
    
    function detectCardType(cardNumber) {
        const patterns = {
            visa: /^4/,
            mastercard: /^5[1-5]/,
            amex: /^3[47]/,
            discover: /^6/
        };
        
        for (const [type, pattern] of Object.entries(patterns)) {
            if (pattern.test(cardNumber)) {
                return type;
            }
        }
        return null;
    }
    
    function addTooltips() {
        // Add tooltips to form fields
        const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
        inputs.forEach(input => {
            if (input.name && input.name.includes('card')) {
                input.title = 'Enter your card number without spaces';
            } else if (input.name && input.name.includes('cvv')) {
                input.title = 'Enter the 3-4 digit security code on the back of your card';
            } else if (input.name && input.name.includes('cardholder')) {
                input.title = 'Enter the name exactly as it appears on your card';
            }
        });
    }
    
    function enhanceButtons() {
        // Find and enhance buttons
        const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
        buttons.forEach(button => {
            // Add loading state
            button.addEventListener('click', function() {
                if (this.textContent.includes('Success')) {
                    this.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing...';
                    this.disabled = true;
                } else if (this.textContent.includes('Failed')) {
                    this.innerHTML = '<i class="fa fa-times"></i> Payment Failed';
                    this.disabled = true;
                }
            });
        });
    }
    
    function addLoadingStates() {
        // Add loading animation to form submission
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing Payment...';
                    submitBtn.disabled = true;
                }
            });
        }
    }
    
    // Add helpful messages
    function addHelpfulMessages() {
        const container = document.querySelector('.card-info-section, form');
        if (container) {
            const helpDiv = document.createElement('div');
            helpDiv.className = 'alert alert-info mt-3';
            helpDiv.innerHTML = `
                <h6><i class="fa fa-info-circle"></i> Payment Tips:</h6>
                <ul class="mb-0">
                    <li>Use the <strong>Success</strong> button to simulate a successful payment</li>
                    <li>Use the <strong>Failed</strong> button to simulate a failed payment</li>
                    <li>This is a test environment - no real money will be charged</li>
                    <li>Your card information is encrypted and secure</li>
                </ul>
            `;
            container.appendChild(helpDiv);
        }
    }
    
    // Call the enhancement function
    setTimeout(addHelpfulMessages, 1000);
    
})();
