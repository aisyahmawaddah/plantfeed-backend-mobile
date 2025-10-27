from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, prodProduct
from .serializers import OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib import messages
from decimal import Decimal
import json
from marketplace.models import prodProduct
from member.models import Person
from basket.models import prodReview
from basket.models import Basket
from basket.serializers import BasketSerializer
from basket.serializers import ProdProductSerializer, PersonSerializer
from django.db import transaction 
from django.core.exceptions import ObjectDoesNotExist
import traceback

# Fetch Order History
@api_view(['GET'])
def history(request):
    user_id = request.GET.get('user_id')

    try:
        # Get the person instance for the user
        person = get_object_or_404(Person, id=user_id)
        
        # Get all baskets related to the user that are checked out
        allBasket = Basket.objects.filter(Person_fk=person.id, is_checkout=True)

        # Retrieve transaction codes from baskets
        transaction_codes = allBasket.values_list('transaction_code', flat=True).distinct()

        # Retrieve associated orders using transaction codes
        associated_orders = Order.objects.filter(transaction_code__in=transaction_codes)

        # Serialize orders to include in the response
        orders_serialized = {
            order.transaction_code: {
                'id': order.id,
                'name': order.name,
                'email': order.email,
                'address': order.address,
                'shipping': order.shipping,
                'total': order.total,
                'status': order.status,
                # Ensure this includes the overall order info
            } for order in associated_orders
        }

        # Serialize baskets and include basket_id and order_info
        allBasket_serialized = []
        for basket in allBasket:
            basket_data = BasketSerializer(basket).data
            transaction_code = basket_data.get('transaction_code')
            order_info = orders_serialized.get(transaction_code, None)  # Get the order_info if exists
            
            # Add order_info to the basket_data if it exists
            if order_info:
                # Include order_info by specifying the fields you need
                basket_data['order_info'] = {
                    'id': order_info['id'],
                    'name': order_info['name'],
                    'email': order_info['email'],
                    'address': order_info['address'],
                    'shipping': order_info['shipping'],
                    'total': order_info['total'],
                    'status': order_info['status'],
                }
            else:
                basket_data['order_info'] = None  # Explicitly set to None if no matching order

            # Change the id to basket_id for clarity
            basket_data['basket_id'] = basket_data.pop('id', None)  # Use basket ID
            allBasket_serialized.append(basket_data)

        return Response({'all_basket': allBasket_serialized}, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@transaction.atomic
def cancel_order(request, basket_id, user_id):
    """
    Cancels all baskets for *the same seller* (Person_fk.id) under one transaction code,
    but leaves baskets from other sellers untouched (partial cancellation).
    """
    # 1) Validate the user
    try:
        user = Person.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response(
            {'message': 'Invalid user ID.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Fetch the basket for this user
    try:
        basket = Basket.objects.get(id=basket_id, Person_fk=user)
    except ObjectDoesNotExist:
        return Response(
            {'message': 'Basket not found or does not belong to this user.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3) Fetch the corresponding order via the transaction code in the basket
    try:
        order = Order.objects.get(transaction_code=basket.transaction_code)
    except ObjectDoesNotExist:
        return Response(
            {'message': 'Order associated with the basket not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 4) If the entire order is already canceled, no further action
    if order.status.lower() == 'cancel':
        return Response(
            {'message': 'Order is already fully canceled.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 5) Identify the "seller" (actually Person_fk) for this basket's product
    #    We'll use the numeric ID.
    seller_id = basket.productid.Person_fk.id

    # 6) Find all baskets under the same transaction code *and* same seller ID
    baskets_to_cancel = Basket.objects.filter(
        transaction_code=basket.transaction_code,
        productid__Person_fk__id=seller_id
    )

    # 7) Mark those baskets as canceled
    baskets_to_cancel.update(status='Cancel')

    # 8) Update product stock/sold for each canceled basket
    for b_item in baskets_to_cancel:
        product = b_item.productid  # This is a prodProduct instance
        product.productStock += b_item.productqty
        product.productSold = max(0, product.productSold - b_item.productqty)
        product.save()

    # 9) Check if there are any baskets left for this transaction code not canceled
    other_baskets_active = Basket.objects.filter(
        transaction_code=basket.transaction_code
    ).exclude(status='Cancel')

    # If none remain, the entire order is effectively canceled
    if not other_baskets_active.exists():
        order.status = 'Cancel'
    else:
        # Some baskets are still active => partial cancel
        order.status = 'Partial Cancel'

    order.save()

    return Response(
        {
            'message': f'Baskets for seller with ID {seller_id} canceled successfully.'
        },
        status=status.HTTP_200_OK
    )
    

@csrf_exempt
@api_view(['POST'])
@transaction.atomic
def complete_order(request, basket_id, user_id):
    """
    Mark as 'Order Received' all baskets for *the same seller* 
    under one transaction code, leaving other sellers' baskets untouched.
    """

    # 1) Ensure user exists
    person = get_object_or_404(Person, id=user_id)

    # 2) Fetch the basket by basket_id, ensuring it belongs to user
    basket = get_object_or_404(Basket, id=basket_id, Person_fk=person)

    # 3) Fetch the associated Order using the transaction_code from the basket
    order = get_object_or_404(Order, transaction_code=basket.transaction_code)

    # 4) Identify the "seller" (assuming prodProduct has Person_fk or similar)
    seller_id = basket.productid.Person_fk.id  # The product's seller

    # 5) Mark only baskets from this transaction code *and* the same seller
    baskets_to_complete = Basket.objects.filter(
        transaction_code=basket.transaction_code,
        productid__Person_fk__id=seller_id
    )

    # If any are already "Order Received," skip them or just ignore
    # For simplicity, we just update them to "Order Received"
    baskets_to_complete.update(status="Order Received")

    # 6) Check if *all* baskets for this transaction code are now "Order Received"
    #    or if some remain active with other sellers
    not_received_yet = Basket.objects.filter(
        transaction_code=basket.transaction_code
    ).exclude(status="Order Received")

    if not not_received_yet.exists():
        # All baskets are received => set the order to 'Order Received'
        order.status = "Order Received"
    else:
        # Partial => only *some* seller's baskets are received
        order.status = "Partial Received"
    order.save()

    return Response(
        {'message': 'Order completed (partially or fully) successfully.'},
        status=status.HTTP_200_OK
    )
    

# Review Product
@api_view(['POST'])
def review_product(request, user_id, basket_id):
    person = get_object_or_404(Person, id=user_id)
    basket = get_object_or_404(Basket, id=basket_id)
    products = Basket.objects.filter(
        transaction_code=basket.transaction_code,
        productid__Person_fk=basket.productid.Person_fk
    )

    reviews_submitted = False
    for product in products:
        # Use productid instead of id
        content = request.data.get(f'review_{product.productid.productid}')  # Correctly access productid
        if content:
            review = prodReview(
                content=content,
                restricted=False,
                Person_fk=person,
                basketid=product,
                productid=product.productid  # Ensure this is correctly referencing the prodProduct instance
            )
            review.save()
            reviews_submitted = True

    if reviews_submitted:
        products.update(status="Product Reviewed")
        return Response({'message': 'Product reviewed successfully.'}, status=status.HTTP_201_CREATED)

    return Response({'message': 'No reviews submitted.'}, status=status.HTTP_400_BAD_REQUEST)


# Invoice
@api_view(['GET'])
def invoice(request, fk1, seller_id):
    user_id = request.GET.get('user_id')  # Retrieve user_id from query parameters
    person = get_object_or_404(Person, id=user_id)

    ids = get_object_or_404(Basket, id=fk1)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    order = get_object_or_404(Order, transaction_code=ids.transaction_code)

    total = sum((bas.productid.productPrice * bas.productqty for bas in basket))
    shipping = sum((bas.productqty * Decimal('5.00') for bas in basket))  # Shipping is RM5.00 per item
    
    final_total = total + shipping
    
    return Response({
        'basket': basket.values(),  # Serialize basket data
        'order': OrderSerializer(order).data,
        'shipping': shipping,
        'final_total': final_total
    }, status=status.HTTP_200_OK)

# Order Again
@api_view(['POST'])
@transaction.atomic
def order_again(request, basket_id, user_id):
    """
    Re-add items from the same seller under the same transaction code
    to the user's active basket(s), ignoring other sellers.
    """

    person = get_object_or_404(Person, id=user_id)

    # 1) Get the reference basket
    reference_basket = get_object_or_404(Basket, id=basket_id, Person_fk=person)

    # 2) Identify the seller
    seller_id = reference_basket.productid.Person_fk.id

    # 3) Find all baskets for the same transaction_code and same seller
    baskets_to_reorder = Basket.objects.filter(
        transaction_code=reference_basket.transaction_code,
        productid__Person_fk__id=seller_id
    )

    # We'll re-create or update each item in the user's *active* basket
    for item in baskets_to_reorder:
        product = item.productid
        qty = item.productqty

        # Check stock
        if product.productStock < qty:
            return Response(
                {'message': f'{product.productName}(s) exceeds available stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there's an existing (non-checked-out) basket entry for this product
        existing_basket = Basket.objects.filter(
            productid=product,
            Person_fk=person,
            is_checkout=False
        ).first()

        if existing_basket:
            # If combining would exceed stock
            if existing_basket.productqty + qty > product.productStock:
                return Response(
                    {'message': f'{product.productName}(s) exceeds available stock limit.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Otherwise, increment the quantity
            existing_basket.productqty += qty
            existing_basket.save()
        else:
            # Create a new basket entry
            Basket.objects.create(
                productqty=qty,
                productid=product,
                Person_fk=person,
                is_checkout=False,
                transaction_code=''  # blank or new code
            )

    return Response(
        {'message': 'The items were re-added to your basket (partially or fully).'},
        status=status.HTTP_200_OK
    )


# Sell History API
@api_view(["GET"])
def sell_history_api(request, fk1):
    try:
        # Check if seller exists
        seller = Person.objects.get(pk=fk1)
        
        # Fetch seller's products
        products = prodProduct.objects.filter(Person_fk=seller)
        product_ids = [product.productid for product in products]
        
        # Fetch baskets with checkout status
        baskets = Basket.objects.filter(productid__in=product_ids, is_checkout=1)
        
        # Extract unique transaction codes
        transactions = baskets.values_list('transaction_code', flat=True).distinct()
        
        # Get orders related to those transactions
        orders = Order.objects.filter(transaction_code__in=transactions)

        # Return empty if no orders are found
        if not orders.exists():
            return Response({
                'status': 'success',
                'message': 'No orders found for this seller.',
                'orders': []
            })

        # Debugging: Log orders found
        print(f"Orders Found: {orders}")

        # Group products by transaction
        products_by_order = {}

        for transaction_code in transactions:
            # Fetch baskets for each transaction
            product_baskets = Basket.objects.filter(
                transaction_code=transaction_code,
                productid__in=product_ids
            )
            products = []
            total_price_for_seller = Decimal('0.00')
            
            for product_basket in product_baskets:
                subtotal = product_basket.productid.productPrice * product_basket.productqty
                total_price_for_seller += subtotal
                
                products.append({
                    "productQty": product_basket.productqty,
                    "productName": product_basket.productid.productName,
                    "productDesc": product_basket.productid.productDesc,
                    "productPrice": product_basket.productid.productPrice,
                    "productCategory": product_basket.productid.productCategory,
                    "orderStatus": product_basket.status,
                })

            # Attach order info if available
            if products:
                order_info = orders.filter(transaction_code=transaction_code).first()
                
                products_by_order[transaction_code] = {
                    "shipping": getattr(order_info, 'shipping', ''),
                    "total": getattr(order_info, 'total', ''),
                    "address": getattr(order_info, 'address', ''),
                    "transaction_code": transaction_code,
                    "buyer_email": getattr(order_info, 'email', ''),
                    "buyer_name": getattr(order_info, 'name', ''),
                    "products": products,
                    "total_price_for_seller": total_price_for_seller,
                    "orderStatus": product_baskets.first().status,
                }

        # Return the response with orders by transaction
        return Response({
            'status': 'success',
            'message': 'Orders retrieved successfully.',
            'orders': products_by_order
        })

    except Person.DoesNotExist:
        # Handle case when the seller is not found
        return Response({
            'status': 'error',
            'message': 'Seller not found.',
            'error_code': 404
        }, status=404)

    except Exception as e:
        # Capture and print the full traceback for debugging
        error_details = traceback.format_exc()
        print(f"Unexpected Error: {e}\n{error_details}")

        # Return the error response
        return Response({
            'status': 'error',
            'message': 'An error occurred while fetching sell history.',
            'error_details': str(e),
            'trace': error_details if request.user.is_superuser else '',  # Show trace for superusers
            'error_code': 500
        }, status=500)
        
@api_view(['POST'])
def update_order_status_api(request):
    try:
        # Print raw body to debug
        print(f"Raw Request Body: {request.body}")

        data = json.loads(request.body)
        print(f"Parsed Data: {data}")

        transaction_code = data.get('transaction_code')
        order_status = data.get('order_status')
        seller_id = data.get('seller_id')

        if not transaction_code or not order_status or not seller_id:
            return Response({'error': 'Missing required fields'}, status=400)

        basket_objs = Basket.objects.filter(transaction_code=transaction_code, productid__Person_fk_id=seller_id)
        
        if not basket_objs.exists():
            return Response({'error': 'Order not found'}, status=404)

        for basket_obj in basket_objs:
            basket_obj.status = order_status
            basket_obj.save()

        return Response({'status': 1, 'message': 'Order status updated successfully'})

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        return Response({'error': 'Invalid JSON format'}, status=400)

    except Exception as e:
        print(f"Exception: {str(e)}")
        return Response({'error': str(e)}, status=500)
