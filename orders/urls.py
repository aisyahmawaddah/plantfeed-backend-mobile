from django.urls import path
from . import api, views
from .api import (
    history,
    cancel_order,
    complete_order,
    review_product,
    invoice,
    order_again,
    sell_history_api,
    update_order_status_api
)

app_name = 'orders'

urlpatterns = [
    path('history.html', views.history, name='history'),
    path('invoice.html/<str:fk1>/<int:seller_id>/', views.invoice, name='invoice'),
    path('order_again/<str:fk1>/<int:seller_id>/', views.order_again, name='order_again'),
    path('complete_order/<str:fk1>/<int:seller_id>/', views.complete_order, name='complete_order'),
    path('cancel_order/<str:fk1>/<int:seller_id>/', views.cancel_order, name='cancel_order'),
    path('SellHistory.html/<int:seller_id>/', views.SellHistory, name='SellHistory'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('review_product/<str:fk1>/<int:seller_id>/', views.review_product, name='review_product'),

    # API Endpoints
    path('api/history/', history, name='api-history'),
    path('api/cancel-order/<int:basket_id>/<int:user_id>/', cancel_order, name='cancel-order'),
    path('api/complete-order/<int:basket_id>/<int:user_id>/', complete_order, name='complete-order'),
    path('api/review_product/<int:user_id>/<int:basket_id>/', review_product, name='review_product'),    path('api/invoice/<str:fk1>/<int:seller_id>/', invoice, name='api-invoice'),
    path('api/order-again/<int:basket_id>/<int:user_id>/', order_again, name='order-again'),
    path('api/sell_history/<int:fk1>/', sell_history_api, name='sell_history_api'),
    path('api/update_order_status/', api.update_order_status_api, name='update_order_status_api'),
]