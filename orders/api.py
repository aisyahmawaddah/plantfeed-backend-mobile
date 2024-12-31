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
def cancel_order(request, order_id, seller_id):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'message': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the buyer (user) and order
    buyer = get_object_or_404(Person, id=user_id)
    order = get_object_or_404(Order, id=order_id)

    # Remove or comment out the authorization check
    # if order.user.id != seller_id:
    #     return Response({'message': 'You do not have permission to cancel this order.'}, status=status.HTTP_403_FORBIDDEN)

    # Check if the order is already canceled
    if order.status.lower() == "cancel":
        return Response({'message': 'Order is already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the order status to "Cancel"
    order.status = "Cancel"
    order.save()

    # Update related OrderItems and Product stock if necessary
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        product = item.product
        product.productStock += item.quantity
        product.productSold = max(product.productSold - item.quantity, 0)
        product.save()

    serializer = OrderSerializer(order)
    return Response({
        'message': 'Order canceled successfully.',
        'order': serializer.data
    }, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status

@csrf_exempt  # This will disable CSRF protection for this view
@api_view(['POST'])
def complete_order(request, order_id, seller_id):
    user_id = request.data.get('user_id')  # Retrieve user_id from body data

    if not user_id:
        return Response({'message': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    person = get_object_or_404(Person, id=user_id)

    # Fetch the Order using the order_id from the URL
    order = get_object_or_404(Order, id=order_id)  # Use order_id instead of fk1

    # Verify that the user_id matches the seller_id
    if person.id != seller_id:
        return Response({'message': 'You do not have permission to complete this order.'}, status=status.HTTP_403_FORBIDDEN)

    # Check if the order is already received
    if order.status.lower() == "order received":
        return Response({'message': 'Order is already marked as received.'}, status=status.HTTP_400_BAD_REQUEST)

    # Update order status to "Order Received"
    order.status = "Order Received"
    order.save()

    # Update all related baskets’ status (assuming baskets are linked to the order somehow)
    baskets = Basket.objects.filter(transaction_code=order.transaction_code, productid__Person_fk_id=seller_id)
    baskets.update(status="Order Received")

    return Response({'message': 'Order completed successfully.'}, status=status.HTTP_200_OK)


# Review Product
@api_view(['POST'])
def review_product(request, fk1, seller_id):
    user_id = request.data.get('user_id')  # Retrieve user_id from body data
    person = get_object_or_404(Person, id=user_id)

    ids = get_object_or_404(Basket, id=fk1)
    products = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)

    if request.method == "POST":   
        for product in products:
            content = request.POST.get(f'review_{product.productid.productid}')
            if content:
                review = prodReview()
                review.content = content
                review.restricted = False
                review.Person_fk = person
                review.basketid = product
                review.productid = product.productid
                review.save()

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
def order_again(request, order_id, seller_id):
    user_id = request.data.get('user_id')  # Retrieve user_id from body data
    person = get_object_or_404(Person, id=user_id)

    # Retrieve the basket by order_id
    ids = get_object_or_404(Basket, id=order_id)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)

    for item in basket:
        product = item.productid
        user = item.Person_fk
        productqty = item.productqty
        
        # Check if the requested quantity exceeds stock
        if product.productStock < productqty:
            return Response({'message': f'{product.productName}(s) exceeds the stock limit in your basket'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the product is already in the user's basket
        existing_basket = Basket.objects.filter(productid=product, Person_fk=user, is_checkout=0).first()

        if existing_basket:  # If the product already exists in the basket
            # If adding the current quantity exceeds stock
            if existing_basket.productqty + productqty > product.productStock:
                return Response({'message': f'{product.productName}(s) exceeds the stock limit in your basket'}, status=status.HTTP_400_BAD_REQUEST)
            existing_basket.productqty += productqty  # Increase the quantity
            existing_basket.save()  # Save changes
            return Response({'message': 'Order quantity successfully updated in your basket'}, status=status.HTTP_200_OK)
        else:
            # Create a new basket entry if it doesn't exist
            Basket.objects.create(productqty=productqty, productid=product, Person_fk=user, is_checkout=0, transaction_code='')
    
    return Response({'message': 'The order was added to your basket.'}, status=status.HTTP_200_OK)


# Sell History
@api_view(['GET'])
def sell_history(request, fk1):
    user_id = request.GET.get('user_id')  # Retrieve user_id from query parameters
    person = get_object_or_404(Person, id=user_id)
    seller = Person.objects.get(pk=fk1)
    products = prodProduct.objects.filter(Person_fk=seller)
    product_ids = [product.productid for product in products]
    baskets = Basket.objects.filter(productid__in=product_ids, is_checkout=1)
    transactions = baskets.values_list('transaction_code', flat=True).distinct()
    orders = Order.objects.filter(transaction_code__in=transactions)

    products_by_order = {}
    
    for transaction_code in transactions:
        product_baskets = Basket.objects.filter(transaction_code=transaction_code, productid__in=product_ids)
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
        
        order_info = orders.filter(transaction_code=transaction_code).first()
        if order_info:  # Ensure order_info exists
            products_by_order[transaction_code] = {
                "shipping": order_info.shipping,
                "total": order_info.total,
                "address": order_info.address,
                "transaction_code": transaction_code,
                "buyer_email": order_info.email,
                "buyer_name": order_info.name,
                "products": products,
                "total_price_for_seller": total_price_for_seller,
                "orderStatus": product_baskets.first().status
            }

    if products_by_order:
        return Response({'products_by_order': products_by_order, 'person': person}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No orders found. Start selling your items!'}, status=status.HTTP_404_NOT_FOUND)

# Update Order History Status
@api_view(['POST'])
def update_order_history_status(request):
    order_id = request.data.get('order_id')
    order_status = request.data.get('order_status')
    seller_id = request.data.get('seller_id')

    try:
        # Check and update the status of the relevant order and basket items
        order = Order.objects.get(id=order_id)
        order.status = order_status
        order.save()

        basket_objs = Basket.objects.filter(transaction_code=order.transaction_code, productid__Person_fk_id=seller_id)
        for basket_obj in basket_objs:
            basket_obj.status = order_status
            basket_obj.save()
        
        return Response({'status': 1, 'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({'status': 0, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'status': 0, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)