# basket/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    checkout,
    basket_summary,
    add_basket_qty,
    remove_basket_qty,
    basket_delete,
    checkout_all
)

app_name = 'basket'

urlpatterns = [
    # API Endpoints
    path('api/checkout/', checkout, name='api-checkout'),
    path('api/basket-summary/', basket_summary, name='api-basket-summary'),
    path('api/add-basket-qty/', add_basket_qty, name='api-add-basket-qty'),
    path('api/remove-basket-qty/', remove_basket_qty, name='api-remove-basket-qty'),
    path('api/basket-delete/', basket_delete, name='api-basket-delete'),
    path('api/checkout-all/', checkout_all, name='api-checkout-all'),

    # Traditional Views
    path('summary.html', views.summary, name='summary'),
    path('add_basket_qty/', views.add_basket_qty, name='add_basket_qty'),
    path('remove_basket_qty/', views.remove_basket_qty, name='remove_basket_qty'),
    path('basket_delete/', views.basket_delete, name='basket_delete'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-all/', views.checkoutAll, name='checkoutAll'),
]