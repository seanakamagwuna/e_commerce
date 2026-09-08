from django.contrib.auth import admin, authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from order.cart import get_cart_items

from .models import Profile


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'product_list'

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            profile, _ = Profile.objects.get_or_create(user=user)
            login(request, user)
            if profile.is_shop_owner:
                return redirect('admin_dashboard')
            return redirect(next_url)

        return render(request, 'login.html', {'error': True, 'next': next_url})

    return render(request, 'login.html', {'next': next_url})


def signup_view(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'product_list'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        error = None
        if not username or not password1:
            error = 'Username and password are required.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            error = 'That username is already taken.'

        if error:
            return render(request, 'signup.html', {
                'error': error,
                'next': next_url,
                'username': username,
                'email': email,
            })

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect(next_url)

    return render(request, 'signup.html', {'next': next_url})

    


def logout_view(request):
    logout(request)
    return redirect('product_list')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if not profile.is_shop_owner:
            profile.address = request.POST.get('address', '').strip()
            profile.phone = request.POST.get('phone', '').strip()
            profile.save()
            return redirect('accounts:profile')

    cart_items, cart_total = get_cart_items(request.session)
    orders = request.user.orders.prefetch_related('items').all()

    return render(request, 'profile.html', {
        'profile': profile,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'orders': orders,
    })

