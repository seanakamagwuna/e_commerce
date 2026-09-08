from types import SimpleNamespace

from store.models import Product


def get_cart_items(session):
    cart = session.get('cart', {})
    items = []
    total = 0

    if cart:
        products = Product.objects.filter(id__in=cart.keys())
        for product in products:
            quantity = cart.get(str(product.id), 0)
            if quantity <= 0:
                continue
            line_total = product.price * quantity
            items.append(SimpleNamespace(product=product, quantity=quantity, line_total=line_total))
            total += line_total

    return items, total


def get_cart_count(session):
    return sum(session.get('cart', {}).values())
