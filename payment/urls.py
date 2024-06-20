from django.urls import path
#from django.conf.urls import url
from . import views

app_name = 'payment'

urlpatterns = [
    path('pay/', views.pay, name='pay'),
    path('stripePayment/', views.checkoutSession, name='checkoutSession'),
    path('success/', views.successCheckout, name='successCheckout'),
    path('cancel/', views.cancelCheckout, name='cancelCheckout'),
    # path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
]