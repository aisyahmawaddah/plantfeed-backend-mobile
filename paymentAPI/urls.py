from django.contrib import admin
from django.urls import path
from paymentAPI.views import ProductLandingPageView, SuccessPageView, CancelPageView, stripe_webhook
from . import views

app_name = 'paymentAPI'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # STRIPE Implementation Try 1
    # path('create-checkout-session', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('create-checkout-session', views.create_checkout_session, name='create-checkout-session'),
    path('', ProductLandingPageView.as_view(), name='landing-page'),
    path('success/', SuccessPageView.as_view(), name='success'),
    path('cancel/', CancelPageView.as_view(), name='cancel'),
    path('webhooks/stripe', stripe_webhook, name='stripe-webhook'),
]