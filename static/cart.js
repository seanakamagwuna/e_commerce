function postForm(form) {
    return fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
    }).then(function (response) {
        if (!response.ok) {
            throw new Error('Request failed');
        }
        return response.json();
    });
}

function updateNavBadge(count) {
    var cartLink = document.querySelector('.nav-cart');
    var badge = document.querySelector('.cart-badge');

    if (count > 0) {
        if (!badge && cartLink) {
            badge = document.createElement('span');
            badge.className = 'cart-badge';
            cartLink.appendChild(badge);
        }
        if (badge) {
            badge.textContent = count;
        }
    } else if (badge) {
        badge.remove();
    }
}

function updateCartTotal(total) {
    var totalEl = document.querySelector('.cart-summary-total');
    if (totalEl) {
        totalEl.textContent = '$' + total;
    }
}

function updateStockBadge(row, stock) {
    var body = row.querySelector('.cart-item-body');
    if (!body) {
        return;
    }
    var badge = body.querySelector('.badge');

    if (stock === 0) {
        if (!badge) {
            badge = document.createElement('span');
            body.appendChild(badge);
        }
        badge.className = 'badge badge-outofstock';
        badge.textContent = 'Out of stock';
    } else if (stock <= 3) {
        if (!badge) {
            badge = document.createElement('span');
            body.appendChild(badge);
        }
        badge.className = 'badge badge-lowstock';
        badge.textContent = 'Only ' + stock + ' left in stock';
    } else if (badge) {
        badge.remove();
    }
}

function showEmptyCart(panel) {
    var list = panel.querySelector('.cart-list');
    var summary = panel.querySelector('.cart-summary');
    if (list) list.remove();
    if (summary) summary.remove();

    var empty = document.createElement('p');
    empty.className = 'cart-empty';
    var shopUrl = panel.dataset.shopUrl || '/';
    empty.innerHTML = 'Your cart is empty. <a href="' + shopUrl + '" class="auth-link">Continue shopping</a>';
    panel.appendChild(empty);
}

function handleAddToCart(form) {
    var button = form.querySelector('button[type="submit"]');
    var originalText = button ? button.textContent : '';

    postForm(form)
        .then(function (data) {
            updateNavBadge(data.cart_item_count);

            if (button && data.added) {
                button.textContent = 'Added';
                button.disabled = true;
                setTimeout(function () {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1200);
            }
        })
        .catch(function () {
            form.submit();
        });
}

function handleCartQtyIncrease(form) {
    var row = form.closest('.cart-item');

    postForm(form)
        .then(function (data) {
            updateNavBadge(data.cart_item_count);
            updateCartTotal(data.cart_total);

            if (!row) return;

            var priceEl = row.querySelector('.cart-item-price');
            var subtotalEl = row.querySelector('.cart-item-subtotal');
            var qtyBtn = row.querySelector('.cart-qty-btn');

            if (priceEl) {
                var unitPrice = priceEl.dataset.unitPrice;
                priceEl.textContent = '$' + unitPrice + ' × ' + data.quantity;
            }
            if (subtotalEl) {
                subtotalEl.textContent = '$' + data.line_total;
            }
            updateStockBadge(row, data.stock);

            if (qtyBtn) {
                qtyBtn.disabled = data.quantity >= data.stock;
            }
        })
        .catch(function () {
            form.submit();
        });
}

function handleCartRemove(form) {
    var row = form.closest('.cart-item');
    var panel = form.closest('.cart-panel');

    postForm(form)
        .then(function (data) {
            updateNavBadge(data.cart_item_count);
            updateCartTotal(data.cart_total);

            if (row) {
                row.remove();
            }
            if (panel && data.cart_item_count === 0) {
                showEmptyCart(panel);
            }
        })
        .catch(function () {
            form.submit();
        });
}

document.addEventListener('submit', function (event) {
    var form = event.target;

    if (form.classList.contains('cart-qty-form')) {
        event.preventDefault();
        handleCartQtyIncrease(form);
    } else if (form.classList.contains('cart-remove-form')) {
        event.preventDefault();
        handleCartRemove(form);
    } else if (form.classList.contains('cart-ajax-form')) {
        event.preventDefault();
        handleAddToCart(form);
    }
});
