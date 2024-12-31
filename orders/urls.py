from django.urls import path
from . import views
from .api import (
    history,
    cancel_order,
    complete_order,
    review_product,
    invoice,
    order_again,
    sell_history,
    update_order_history_status
)

app_name = 'orders'

urlpatterns = [
    path('history.html', views.history, name='history'),
    path('invoice.html/<str:fk1>/<int:seller_id>/', views.invoice, name='invoice'),
    path('order_again/<str:fk1>/<int:seller_id>/', views.order_again, name='order_again'),
    path('complete_order/<str:fk1>/<int:seller_id>/', views.complete_order, name='complete_order'),
    path('cancel_order/<str:fk1>/<int:seller_id>/', views.cancel_order, name='cancel_order'),
    path('SellHistory.html/<str:fk1>/', views.SellHistory, name="SellHistory"),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('review_product/<str:fk1>/<int:seller_id>/', views.review_product, name='review_product'),

    # API Endpoints
    path('api/history/', history, name='api-history'),
    path('api/cancel_order/<int:order_id>/<int:seller_id>/', cancel_order, name='api-cancel-order'),
    path('orders/api/complete_order/<int:order_id>/<int:seller_id>/', complete_order, name='api-complete-order'),
    path('api/review_product/<str:fk1>/<int:seller_id>/', review_product, name='api-review-product'),
    path('api/invoice/<str:fk1>/<int:seller_id>/', invoice, name='api-invoice'),
    path('api/order_again/<int:order_id>/<int:seller_id>/', order_again, name='order-again'),
    path('api/sell_history/<str:fk1>/', sell_history, name='api-sell-history'),
    path('api/update_order_status/', update_order_history_status, name='api-update-order-status'),
]