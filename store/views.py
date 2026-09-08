from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.text import slugify

from order.models import Order

from .models import Category, Product

# Create your views here.
def product_list(request):
    all_products = Product.objects.all().order_by('-id')
    categories = Category.objects.all()
    return render(request, 'home.html', {'all_products': all_products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

def category_detail(request, slug):
    pass
def admin_dashboard(request):
    if not getattr(request.user.profile, 'is_shop_owner', False):
        return redirect('product_list')
    products = Product.objects.all().order_by('-id')
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    return render(request, 'admin_dashboard.html', {
        'products': products,
        'categories': categories,
        'orders': orders,
    })

@login_required
def add_product(request):
    if not getattr(request.user.profile, 'is_shop_owner', False):
        return redirect('product_list')

    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        stock = request.POST.get('stock', '').strip()

        if not all([name, price, description, category_id, image]):
            error = 'Please fill in all fields and choose an image.'
        else:
            try:
                product = Product.objects.create(
                    name=name,
                    slug=slugify(name),
                    description=description,
                    price=price,
                    image=image,
                    stock=stock,
                )
                product.Category.set([category_id])
                return redirect('admin_dashboard')
            except (IntegrityError, ValueError):
                error = 'A product with that name already exists, or the price is invalid.'

    return render(request, 'add_product.html', {'categories': Category.objects.all(), 'error': error})

@login_required
def edit_product(request, slug):
    if not getattr(request.user.profile, 'is_shop_owner', False):
        return redirect('product_list')

    product = get_object_or_404(Product, slug=slug)
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        stock = request.POST.get('stock', '').strip()

        if not all([name, price, description, category_id, stock]):
            error = 'Please fill in all fields.'
        else:
            try:
                product.name = name
                product.price = price
                product.description = description
                product.stock = stock
                if image:
                    product.image = image
                product.save()
                product.Category.set([category_id])
                return redirect('admin_dashboard')
            except (IntegrityError, ValueError):
                error = 'A product with that name already exists, or the price is invalid.'

    current_category = product.Category.first()
    return render(request, 'edit_product.html', {
        'product': product,
        'categories': Category.objects.all(),
        'current_category_id': current_category.id if current_category else None,
        'error': error,
    })

@login_required
def delete_product(request, slug):
    if not getattr(request.user.profile, 'is_shop_owner', False):
        return redirect('product_list')

    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        product.image.delete(save=False)
        product.delete()

    return redirect('admin_dashboard')

def search(request):
    query = request.GET.get('q', '').strip()
    results = Product.objects.none()
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query)
        ).distinct()
    return render(request, 'search.html', {'query': query, 'results': results})

