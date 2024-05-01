from django.urls import path
#from django.conf.urls import url
from . import views

app_name = 'orders'

urlpatterns = [
    path('history.html', views.history, name='history'),
    path('invoice.html/<str:fk1>/', views.invoice, name='invoice'),
    path('order_again/<str:transaction_code>/', views.order_again, name='order_again'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('SellHistory.html/<str:fk1>/',views.SellHistory, name="SellHistory"),
    path('update_order_status/',views.update_order_status, name='update_order_status'),
]