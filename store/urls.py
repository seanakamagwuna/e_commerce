from django.db import models
from . import views
from django.urls import path

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('product/<slug:slug>/edit/', views.edit_product, name='edit_product'),
    path('product/<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('search/', views.search, name='search'),
]