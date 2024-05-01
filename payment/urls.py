from django.urls import path
#from django.conf.urls import url
from . import views

app_name = 'payment'

urlpatterns = [
    path('pay', views.pay, name='pay'),
]