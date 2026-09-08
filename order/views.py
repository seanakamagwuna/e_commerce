from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profile
from store.models import Product

from .cart import get_cart_count, get_cart_items
from .models import Order, OrderItem

# Create your views here.
def cart_detail(request):
    return redirect('accounts:profile')

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    added = False

    if request.method == 'POST' and product.stock > 0:
        cart = request.session.setdefault('cart', {})
        key = str(product_id)
        before = cart.get(key, 0)
        cart[key] = min(before + 1, product.stock)
        request.session.modified = True
        added = cart[key] > before

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        quantity = request.session.get('cart', {}).get(str(product_id), 0)
        _, cart_total = get_cart_items(request.session)
        return JsonResponse({
            'added': added,
            'cart_item_count': get_cart_count(request.session),
            'product_id': product.id,
            'quantity': quantity,
            'stock': product.stock,
            'line_total': str(product.price * quantity),
            'cart_total': str(cart_total),
        })

    return redirect(request.META.get('HTTP_REFERER') or 'product_list')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.setdefault('cart', {})
        cart.pop(str(product_id), None)
        request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        _, cart_total = get_cart_items(request.session)
        return JsonResponse({
            'removed': True,
            'cart_item_count': get_cart_count(request.session),
            'product_id': product_id,
            'cart_total': str(cart_total),
        })

    return redirect(request.META.get('HTTP_REFERER') or 'accounts:profile')

@login_required
def checkout(request):
    cart_items, cart_total = get_cart_items(request.session)

    if not cart_items:
        return redirect('accounts:profile')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    error = None

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not address or not phone:
            error = 'Address and phone are required.'
        else:
            cart_items, cart_total = get_cart_items(request.session)
            if not cart_items:
                return redirect('accounts:profile')

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    phone=phone,
                    total=cart_total,
                )
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                    item.product.stock = max(item.product.stock - item.quantity, 0)
                    item.product.save(update_fields=['stock'])

                profile.address = address
                profile.phone = phone
                profile.save()

            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order:order_confirmation', order_id=order.id)

    return render(request, 'checkout.html', {
        'profile': profile,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'error': error,
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})
