from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings
from marketplace.models import prodProduct
from orders.models import Order
from member.models import Person
from basket.models import Basket
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return Response({'error': 'Invalid payload or signature'}, status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        customer_email = session["customer_details"]["email"]
        product_ids = session["metadata"].get("product_ids", "").split(',')
        
        products = prodProduct.objects.filter(productid__in=product_ids)
        # Handle order fulfillment
        for prod in products:
            # Send confirmation email
            send_mail(
                subject='Order Confirmation',
                message=f"Thank you for your order. Your order has been successfully placed.",
                recipient_list=[customer_email],
                from_email=settings.EMAIL_HOST_USER
            )

        fulfill_order(session.line_items)
        
    return HttpResponse(status=200)

def fulfill_order(line_items):
    # Implement order fulfillment logic
    print("Fulfilling order")


@api_view(['GET'])
def get_payment_status(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({'error': 'Session ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return Response({'status': session.payment_status}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'error': f'Error retrieving session: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)