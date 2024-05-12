from django.urls import path

from . import views

app_name = 'basket'

urlpatterns = [
    path('summary.html', views.summary, name='summary'),
    path('add_basket_qty/', views.add_basket_qty, name='add_basket_qty'),
    path('remove_basket_qty/', views.remove_basket_qty, name='remove_basket_qty'),
    path('basket_delete/', views.basket_delete, name='basket_delete'),
    #09/05/2024
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-all/', views.checkoutAll, name='checkoutAll'),
    #09/05/2024
]