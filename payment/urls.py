from django.urls import path
#from django.conf.urls import url
from . import views
from . import api

app_name = 'payment'

urlpatterns = [
    path('pay/', views.pay, name='pay'),
    path('stripePayment/', views.checkoutSession, name='checkoutSession'),
    path('success/', views.successCheckout, name='successCheckout'),
    path('cancel/', views.cancelCheckout, name='cancelCheckout'),
    # path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),


    path('api/create-checkout-session/', api.create_checkout_session, name='create-checkout-session'),
    path('api/process-payment/', api.process_payment, name='process-payment'),
    path('api/create-payment-intent/', api.create_payment_intent, name='create-payment-intent'),
]