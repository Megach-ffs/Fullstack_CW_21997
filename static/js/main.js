

document.addEventListener('DOMContentLoaded', function () {


    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            let isValid = true;

            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, 'This field is required');
                } else {
                    clearFieldError(field);
                }
            });

            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                if (field.value && !isValidEmail(field.value)) {
                    isValid = false;
                    showFieldError(field, 'Please enter a valid email address');
                }
            });

            const passwordFields = form.querySelectorAll('input[type="password"]');
            if (passwordFields.length > 0) {
                const password = passwordFields[0];
                if (password.value && password.value.length < 8) {
                    isValid = false;
                    showFieldError(password, 'Password must be at least 8 characters');
                }
            }

            const password1 = form.querySelector('input[name="password1"]');
            const password2 = form.querySelector('input[name="password2"]');
            if (password1 && password2) {
                if (password1.value !== password2.value) {
                    isValid = false;
                    showFieldError(password2, 'Passwords do not match');
                }
            }


            const phoneField = form.querySelector('input[name="phone"]');
            if (phoneField && phoneField.value) {
                if (!isValidPhone(phoneField.value)) {
                    isValid = false;
                    showFieldError(phoneField, 'Please enter a valid phone number');
                }
            }

            if (!isValid) {
                e.preventDefault();
                showFormError('Please correct the errors below');
            } else {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }
            }
        });

        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateField(this);
            });

            input.addEventListener('input', function () {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });

    function validateField(field) {
        clearFieldError(field);

        if (field.hasAttribute('required') && !field.value.trim()) {
            showFieldError(field, 'This field is required');
            return false;
        }

        if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }

        if (field.type === 'password' && field.value && field.value.length < 8) {
            showFieldError(field, 'Password must be at least 8 characters');
            return false;
        }

        if (field.name === 'phone' && field.value && !isValidPhone(field.value)) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }

        field.classList.add('is-valid');
        return true;
    }

    function showFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    function showFormError(message) {
        let alertDiv = document.querySelector('.form-validation-alert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show form-validation-alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            const mainContent = document.querySelector('main');
            if (mainContent) {
                mainContent.insertBefore(alertDiv, mainContent.firstChild);
            }
        }
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function isValidPhone(phone) {
        const re = /^[\d\s\-\+\(\)]{10,}$/;
        return re.test(phone);
    }

    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && targetId !== '#!') {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    const clickableRows = document.querySelectorAll('tr[data-href]');
    clickableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function () {
            window.location.href = this.getAttribute('data-href');
        });
    });

    const loadingLinks = document.querySelectorAll('a[data-loading]');
    loadingLinks.forEach(link => {
        link.addEventListener('click', function () {
            this.classList.add('btn-loading');
        });
    });

    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted';
        counter.textContent = `0 / ${maxLength} characters`;
        textarea.parentElement.appendChild(counter);

        textarea.addEventListener('input', function () {
            const currentLength = this.value.length;
            counter.textContent = `${currentLength} / ${maxLength} characters`;

            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    });

    
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const form = this.closest('form');
                if (form && this.value.length >= 3) {
                    form.submit();
                }
            }, 500);
        });
    }

});
