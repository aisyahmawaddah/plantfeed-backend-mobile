from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from basket.models import Basket
from marketplace.models import prodProduct
from member.models import Person
from .serializers import BasketSerializer  # Import the BasketSerializer here
import json
from .models import Basket 
from django.shortcuts import get_object_or_404
from django.conf import settings  # Import settings

# Summary of items in the basket
@api_view(['GET'])
def basket_summary(request):
    user_id = request.GET.get('user_id')

    try:
        person = Person.objects.get(id=user_id)
        all_basket_items = Basket.objects.filter(Person_fk=person, is_checkout=0)

        basket_data = []
        total = 0

        for basket_item in all_basket_items:
            product = basket_item.productid  # Product object linked to this basket item
            seller = product.Person_fk  # Person object who is the seller of this product

            basket_data.append({
                "id": basket_item.id,
                "productqty": basket_item.productqty,
                "productid": {
                    "productid": product.productid,
                    "productName": product.productName,
                    "productDesc": product.productDesc,
                    "productCategory": product.productCategory,
                    "productPrice": str(product.productPrice),  # Ensure it's JSON serializable
                    "productStock": product.productStock,
                    "productPhoto": product.productPhoto.url if product.productPhoto else None,
                    "productRating": product.productRating,
                    "productSold": product.productSold,
                    "timePosted": product.timePosted,
                    "restricted": product.restricted
                },
                "buyer_info": {
                    "id": person.id,
                    "Username": person.Username,
                    "Email": person.Email,
                },
                "seller_info": {
                    "id": seller.id,
                    "Username": seller.Username,
                    "Email": seller.Email,
                },
                "is_checkout": basket_item.is_checkout,
                "transaction_code": basket_item.transaction_code,
                "status": basket_item.status
            })

            total += product.productPrice * basket_item.productqty

        return Response({'all_basket': basket_data, 'total': total}, status=status.HTTP_200_OK)
    
    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    

# Add quantity to an item in the basket
@api_view(['POST'])
def add_basket_qty(request):
    item_id = request.data.get('item_id')
    
    try:
        basket_obj = Basket.objects.get(id=item_id)
        prod_obj = prodProduct.objects.get(productid=basket_obj.productid.productid)

        if prod_obj.productStock > basket_obj.productqty:
            basket_obj.productqty += 1
            basket_obj.save()
            return Response({'status': 1, 'message': 'Quantity increased successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 0, 'message': 'Not enough stock for this product.'}, status=status.HTTP_400_BAD_REQUEST)

    except Basket.DoesNotExist:
        return Response({'error': 'Basket item does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

# Remove quantity from an item in the basket
@api_view(['POST'])
def remove_basket_qty(request):
    item_id = request.data.get('item_id')

    try:
        obj = Basket.objects.get(id=item_id)
        if obj.productqty > 1:
            obj.productqty -= 1
            obj.save()
        else:
            obj.delete()

        return Response({'status': 1, 'message': 'Quantity decreased successfully.'}, status=status.HTTP_200_OK)

    except Basket.DoesNotExist:
        return Response({'error': 'Basket item does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def basket_delete(request):
    item_id = request.query_params.get('item_id')  # Use query parameters

    if not item_id:
        return Response({'error': 'item_id not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = Basket.objects.get(id=item_id)
        obj.delete()
        return Response({'status': 1, 'message': 'Item deleted from the basket successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except Basket.DoesNotExist:
        return Response({'error': 'Basket item does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def checkout(request):
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        person = get_object_or_404(Person, id=user_id)
        selected_product_ids = request.data.get('selected_products', [])
        
        if not selected_product_ids:
            return Response({'error': 'No products found for checkout'}, status=status.HTTP_400_BAD_REQUEST)

        selected_products = Basket.objects.filter(
            id__in=selected_product_ids,
            Person_fk=person.id,
            is_checkout=0
        )

        if not selected_products:
            return Response({'error': 'No valid basket items found for checkout'}, status=status.HTTP_404_NOT_FOUND)

        subtotals = {}
        seller_totals = {}
        product_details = {}

        for basket in selected_products:
            product = basket.productid  # Get the product associated with the basket item
            seller = product.Person_fk  # This is the seller
            seller_name = seller.Name  # Get seller's name

            # Calculate subtotal for this product
            subtotal = product.productPrice * basket.productqty
            seller_totals[seller_name] = seller_totals.get(seller_name, 0) + subtotal
            
            subtotals[basket.id] = subtotal
            
            # Store additional product details
            product_details[basket.id] = {
                'name': product.productName,
                'photo': product.productPhoto.url if product.productPhoto else None,
                'quantity': basket.productqty,
                'seller_name': seller_name,
                'unit_price': product.productPrice
            }

        # Total checkout amount without shipping fee
        total_checkout = sum(seller_totals.values())

        return Response({
            'totalCheckout': total_checkout,  # does not include shipping
            'subtotals': subtotals,
            'sellerTotals': seller_totals,
            'product_details': product_details,
            'totalShippingFee': 0,  # Remove or set to 0 if frontend handles shipping
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        }, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def checkout_all(request):
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        person = get_object_or_404(Person, id=user_id)
        
        selected_products = Basket.objects.filter(Person_fk=person.id, is_checkout=0)
        
        if not selected_products:
            return Response({'error': 'No products to checkout'}, status=status.HTTP_404_NOT_FOUND)

        subtotals = {}
        seller_totals = {}
        product_details = {}

        for basket in selected_products:
            product = basket.productid  # Get the product associated with the basket item
            seller = product.Person_fk   # This is the seller
            
            seller_name = seller.Name  # Get seller's name

            # Calculate subtotal for this product
            subtotal = product.productPrice * basket.productqty
            seller_totals[seller_name] = seller_totals.get(seller_name, 0) + subtotal
            
            subtotals[basket.id] = subtotal
            
            # Store additional product details
            product_details[basket.id] = {
                'name': product.productName,
                'photo': product.productPhoto.url if product.productPhoto else None,
                'quantity': basket.productqty,
                'seller_name': seller_name
            }

        # Total checkout amount without shipping fee
        total_checkout = sum(seller_totals.values())

        return Response({
            'totalCheckout': total_checkout,  # does not include shipping
            'subtotals': subtotals,
            'sellerTotals': seller_totals,
            'product_details': product_details,
            'totalShippingFee': 0,  # Remove or set to 0 if frontend handles shipping
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        }, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

