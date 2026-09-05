document.addEventListener('DOMContentLoaded', function() {
    // Cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.product;
            const quantity = document.getElementById('quantity')?.value || 1;
            fetch('/api/v1/cart/add-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ product_id: productId, quantity: parseInt(quantity) }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount(data.cart.total_items_count);
                    showNotification('Item added to cart!');
                }
            });
        });
    });

    // Quantity controls
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.qty-input');
            let value = parseInt(input.value);
            if (this.dataset.action === 'increase') value++;
            else if (this.dataset.action === 'decrease' && value > 1) value--;
            input.value = value;
            input.dispatchEvent(new Event('change'));
        });
    });

    // Cart quantity update
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', function() {
            const itemId = this.dataset.item;
            fetch('/api/v1/cart/update-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ item_id: itemId, quantity: parseInt(this.value) }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) location.reload();
            });
        });
    });

    // Remove from cart
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.item;
            fetch('/api/v1/cart/remove-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ item_id: itemId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) location.reload();
            });
        });
    });

    // Apply coupon
    const applyCouponBtn = document.getElementById('apply-coupon');
    if (applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function() {
            const code = document.getElementById('coupon-code').value;
            fetch('/api/v1/cart/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ code: code }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Coupon applied!');
                    location.reload();
                } else {
                    showNotification(data.error?.message || 'Invalid coupon', 'error');
                }
            });
        });
    }

    // Product tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            this.classList.add('active');
            document.getElementById(this.dataset.tab).style.display = 'block';
        });
    });

    // Search autocomplete
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value;
                if (query.length >= 2) {
                    fetch(`/api/v1/autocomplete/?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            // Show autocomplete suggestions
                        });
                }
            }, 300);
        });
    }

    // Variant selector
    const variantSelect = document.getElementById('variant-select');
    if (variantSelect) {
        variantSelect.addEventListener('change', function() {
            const option = this.options[this.selectedIndex];
            const price = option.dataset.price;
            const stock = option.dataset.stock;
            document.querySelector('.current-price').textContent = `$${price}`;
        });
    }
});

function getCookie(name) {
    let value = null;
    document.cookie.split(';').forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            value = decodeURIComponent(cookie.substring(name.length + 1));
        }
    });
    return value;
}

function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) cartCount.textContent = count;
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 15px 25px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white; border-radius: 5px; z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function changeMainImage(src) {
    document.getElementById('main-product-image').src = src;
}
