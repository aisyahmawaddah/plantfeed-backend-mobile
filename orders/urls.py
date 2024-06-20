from django.urls import path
#from django.conf.urls import url
from . import views

app_name = 'orders'

urlpatterns = [
    path('history.html', views.history, name='history'),
    path('invoice.html/<str:fk1>/<int:seller_id>/', views.invoice, name='invoice'),
    path('order_again/<str:fk1>/<int:seller_id>/', views.order_again, name='order_again'),
    path('complete_order/<str:fk1>/<int:seller_id>/', views.complete_order, name='complete_order'),
    path('cancel_order/<str:fk1>/<int:seller_id>/', views.cancel_order, name='cancel_order'),
    path('SellHistory.html/<str:fk1>/',views.SellHistory, name="SellHistory"),
    path('update_order_status/',views.update_order_status, name='update_order_status'),
    path('review_product/<str:fk1>/<int:seller_id>/', views.review_product, name='review_product')
]