from django.contrib import admin
from django.urls import path
from django.urls import re_path as url, include
# from LOGIN import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from LOGIN.views import UserReg, sharing, discussion, view, workshop, booking, member
from .import views
# from .import index
from .views import *
# from .api import UserList, UserDetail, UserAuthentication

from django.urls import path
from .api import (
    list_products,
    view_product,
    add_to_basket,
    buy_now,
    view_seller,
    update_product,
    delete_product,
    get_product_reviews,
    sell_product
)

app_name = 'marketplace'

urlpatterns = [
    # Traditional views
    path('MainMarketplace', views.mainMarketplace, name="MainMarketplace"),
    path('SellProduct.html/<str:fk1>/', views.sellProduct, name="SellProduct"),
    path('DeleteProduct/<str:fk1>/', views.deleteProduct, name="DeleteProduct"),
    path('DeleteProduct2/<str:fk1>/', views.deleteProduct2, name="DeleteProduct2"),
    path('UpdateProduct.html/<str:fk1>/', views.updateProduct, name="UpdateProduct"),
    path('MyMarketplace', views.myMarketplace, name="MyMarketplace"),
    path('buy_now/<str:fk1>/<str:fk2>/', views.buy_now, name='buy_now'),
    path('add_to_basket/<str:fk1>/<str:fk2>/', views.add_to_basket, name='add_to_basket'),
    path('ViewProduct/<str:pk>', views.viewProduct, name="viewProduct"),
    path('ViewSeller/<str:pk>', views.viewSeller, name="viewSeller"),
    path('RestrictProduct/<str:fk1>/', views.restrictProduct, name="restrictProduct"),
    path('UnrestrictProduct/<str:fk1>/', views.unrestrictProduct, name="unrestrictProduct"),

    # API Endpoints
    path('api/products/', list_products, name='api-product-list'),  # List all products
    path('api/products/view/<int:product_id>/', view_product, name='api-product-detail'),  # View a single product
    path('api/add-to-basket/', add_to_basket, name='api-add-to-basket'),  # Add product to basket
    path('api/buy-now/', buy_now, name='api-buy-now'),  # Buy now functionality
    path('api/seller/<int:seller_id>/', view_seller, name='api-view-seller'),  # View seller information
    path('api/products/<int:product_id>/update/', update_product, name='api-update-product'),  # Update product info
    path('api/products/<int:product_id>/delete/', delete_product, name='api-delete-product'),  # Delete product
    path('api/products/<int:product_id>/reviews/', get_product_reviews, name='api-get-reviews'),  # Get product reviews
    path('api/sell_product/<int:fk1>/', sell_product, name='sell_product'),
]

