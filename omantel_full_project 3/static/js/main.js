document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality for bill payment page
    const tabs = document.querySelectorAll('.tab');
    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Show corresponding form
                const tabType = this.getAttribute('data-tab');
                const forms = document.querySelectorAll('.tab-form');
                forms.forEach(form => {
                    if (form.getAttribute('id') === tabType + '-form') {
                        form.style.display = 'block';
                    } else {
                        form.style.display = 'none';
                    }
                });
            });
        });
    }

    // Input validation for phone number fields
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Limit to reasonable phone number length
            if (this.value.length > 12) {
                this.value = this.value.slice(0, 12);
            }
            
            // Change the button color if phone number is exactly 8 digits
            const form = this.closest('form');
            if (form) {
                const checkBtn = form.querySelector('button[name="check_bill"]');
                if (checkBtn) {
                    if (this.value.length === 8) {
                        checkBtn.classList.remove('btn-secondary');
                        checkBtn.classList.add('btn-primary');
                    } else {
                        checkBtn.classList.remove('btn-primary');
                        checkBtn.classList.add('btn-secondary');
                    }
                }
            }
        });
    });

    // Input validation for amount fields
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers and a single decimal point
            this.value = this.value.replace(/[^0-9.]/g, '');
            
            // Ensure only one decimal point
            const parts = this.value.split('.');
            if (parts.length > 2) {
                this.value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Limit amount to 100
            const numValue = parseFloat(this.value);
            if (!isNaN(numValue) && numValue > 100) {
                this.value = '100';
            }
        });
    });

    // Credit card form validation
    const cardForm = document.getElementById('payment-form');
    if (cardForm) {
        const cardNumberInput = document.getElementById('card_number');
        const expiryInput = document.getElementById('expiry');
        const cvvInput = document.getElementById('cvv');
        
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function() {
                // Allow only numbers and format with spaces
                let value = this.value.replace(/[^0-9]/g, '');
                
                // Add spaces after every 4 digits
                let formattedValue = '';
                for (let i = 0; i < value.length; i++) {
                    if (i > 0 && i % 4 === 0) {
                        formattedValue += ' ';
                    }
                    formattedValue += value[i];
                }
                
                // Limit to 16 digits (plus spaces)
                if (value.length > 16) {
                    value = value.slice(0, 16);
                    formattedValue = formattedValue.slice(0, 19); // 16 digits + 3 spaces
                }
                
                this.value = formattedValue;
            });
        }
        
        if (expiryInput) {
            expiryInput.addEventListener('input', function() {
                // Allow only numbers and format as MM/YY
                let value = this.value.replace(/[^0-9]/g, '');
                
                if (value.length > 0) {
                    // Format as MM/YY
                    if (value.length > 2) {
                        value = value.slice(0, 2) + '/' + value.slice(2);
                    }
                    
                    // Limit to 4 digits (MM/YY)
                    if (value.length > 5) {
                        value = value.slice(0, 5);
                    }
                }
                
                this.value = value;
            });
        }
        
        if (cvvInput) {
            cvvInput.addEventListener('input', function() {
                // Allow only numbers
                this.value = this.value.replace(/[^0-9]/g, '');
                
                // Limit to exactly 3 digits
                if (this.value.length > 3) {
                    this.value = this.value.slice(0, 3);
                }
            });
        }
    }

    // OTP input validation
    const otpInput = document.getElementById('otp');
    if (otpInput) {
        otpInput.addEventListener('input', function() {
            // Allow only numbers
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
});
