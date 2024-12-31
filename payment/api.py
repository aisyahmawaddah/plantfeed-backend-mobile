from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings
from marketplace.models import prodProduct
from orders.models import Order, OrderItem
from member.models import Person
from basket.models import Basket
from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        person = get_object_or_404(Person, id=user_id)
        product_ids = request.data.get('selected_products', [])
        shipping_details = request.data.get('shipping_details', {})  # New: retrieve shipping details

        if not product_ids:
            return Response({'error': 'No products found for checkout'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter basket items based on user and selected product IDs
        products = Basket.objects.filter(id__in=product_ids, Person_fk=person, is_checkout=0)

        if not products.exists():
            return Response({'error': 'No valid basket items found for checkout'}, status=status.HTTP_404_NOT_FOUND)

        line_items = []
        for product in products:
            description = product.productid.productDesc if product.productid.productDesc else "No description available"
            line_items.append({
                'price_data': {
                    'currency': 'myr',
                    'unit_amount': int((product.productid.productPrice) * 100),  # Price excluding shipping
                    'product_data': {
                        'name': product.productid.productName,
                        'description': description,
                    },
                },
                'quantity': product.productqty,
            })

        YOUR_DOMAIN = "http://your-live-domain.com"  # Replace with your actual domain

        # Create the Stripe checkout session with shipping address collection
        checkout_session = stripe.checkout.Session.create(
            customer_email=person.Email,
            shipping_address_collection={
                'allowed_countries': ['MY', 'SG', 'ID', 'TH', 'BN'],
            },
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{YOUR_DOMAIN}/pay/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/cancel/",
            metadata={
                'selected_product_ids': ','.join(map(str, product_ids)),
                'shipping_details': json.dumps(shipping_details)  # New: send the shipping details as metadata
            }
        )

        # Return the checkout session ID in the response
        return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def process_payment(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({'error': 'No session ID provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve Stripe session
        session = stripe.checkout.Session.retrieve(session_id)

        # Extract metadata and user email
        selected_product_ids = session.metadata.get('selected_product_ids', '').split(',')
        person = Person.objects.get(Email=session.customer_email)

        # Generate transaction code
        transaction_code = 'TRANS#' + str(timezone.now())
        order_status = "Payment Made"

        # Retrieve the shipping details from the metadata
        shipping_details = json.loads(session.metadata.get('shipping_details', '{}'))
        address = shipping_details.get('address', '')

        # Update the database for the selected products
        selected_products = Basket.objects.filter(id__in=selected_product_ids)
        sellers = set()  # Set to keep track of unique sellers
        product_total = 0  # Variable to accumulate total product price

        for bas in selected_products:
            product = bas.productid  # Get the product
            seller = product.Person_fk  # Assuming Person_fk is the seller

            sellers.add(seller)  # Add seller to sellers set

            # Update product stock and sold count
            product_obj = get_object_or_404(prodProduct, productid=product.productid)
            product_obj.productStock -= bas.productqty
            product_obj.productSold += bas.productqty

            if product_obj.productStock < 0:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

            product_obj.save()

            # Update basket to mark as checked out
            bas.is_checkout = 1
            bas.transaction_code = transaction_code
            bas.status = order_status
            bas.save()

            # Calculate total product price
            product_total += product_obj.productPrice * bas.productqty

        # Calculate shipping cost: RM 5 for each unique seller
        shipping_cost = len(sellers) * 5  # RM 5 per unique seller

        # Calculate final total
        total_amount = product_total + shipping_cost  # Total including products and shipping

        # Create Order instance with calculated total amount
        order = Order.objects.create(
            name=person.Name,
            email=person.Email,
            transaction_code=transaction_code,
            total=total_amount,  # Store total which includes shipping
            status=order_status,
            user=person,
            address=address,
            shipping=shipping_cost  # You can store shipping separately if you want
        )

        # Create OrderItem entry for each product in the order
        for bas in selected_products:
            OrderItem.objects.create(
                order=order,
                product=bas.productid,
                price=bas.productid.productPrice,
                quantity=bas.productqty
            )

        return Response({'status': 'Payment processed successfully', 'order_id': order.id}, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST'])
def create_payment_intent(request):
    try:
        # Retrieve user_id from query parameters
        user_id = request.GET.get('user_id')

        if not user_id:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the person instance by user_id
        person = get_object_or_404(Person, id=user_id)
        
        # Retrieve product_ids from the request body
        product_ids = request.data.get('selected_products', [])

        if not product_ids:
            return Response({'error': 'No products found for checkout'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter basket items based on user and selected product IDs
        products = Basket.objects.filter(id__in=product_ids, Person_fk=person, is_checkout=0)

        if not products.exists():
            return Response({'error': 'No valid basket items found for checkout'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate total amount in cents
        total_amount = 0
        
        # Set shipping cost per item
        shipping_cost_per_item = 500  # RM 5.00 (in cents)

        for product in products:
            subtotal = product.productid.productPrice * 100 * product.productqty  # Total price for each product
            total_amount += subtotal + (shipping_cost_per_item * product.productqty)  # Add shipping per item

        # Log the total amount for debugging
        print(f"Total amount (with shipping per item): {total_amount} cents")

        # Create the Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_amount),
            currency='myr',
            receipt_email=person.Email,
        )

        return Response({'client_secret': payment_intent['client_secret']}, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)