from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import prodProduct, Person
from basket.models import Basket, prodReview
from member.models import Person
from django.db.models import Sum, Q, DecimalField, ExpressionWrapper, Max, F, Count
from .serializers import ProductSerializer, ReviewSerializer
from django.http import JsonResponse
import re
from django.shortcuts import get_object_or_404
from urllib.parse import urljoin
from django.conf import settings

# Endpoint for Marketplace
@api_view(['GET'])
def list_products(request):
    products = prodProduct.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_product(request, product_id):
    try:
        # Get the product
        product = prodProduct.objects.get(productid=product_id)
        
        # Serialize the product data
        product_serializer = ProductSerializer(product)
        
        # Fetch reviews for this product
        reviews = prodReview.objects.filter(productid_id=product_id)
        
        # Serialize the reviews
        reviews_serializer = ReviewSerializer(reviews, many=True)
        
        # Add the serialized reviews to the product data
        product_data = product_serializer.data
        product_data['reviews'] = reviews_serializer.data  # Add reviews to the response
        
        return Response(product_data, status=status.HTTP_200_OK)
    except prodProduct.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['POST'])
def add_to_basket(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(Person, id=user_id)
        product = prodProduct.objects.get(productid=product_id)

        if product.productStock < quantity:
            return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        # Manually replicate "get or create" logic
        try:
            basket_item = Basket.objects.get(
                productid=product,
                Person_fk=user,
                is_checkout=False
            )
            # If found, increment quantity
            basket_item.productqty += quantity
        except Basket.DoesNotExist:
            # If not found, create new basket record
            basket_item = Basket(
                productid=product,
                Person_fk=user,
                is_checkout=False,
                productqty=quantity
            )

        basket_item.save()  # calls the custom save() without force_insert
        return Response({'message': 'Product added to basket'}, status=status.HTTP_201_CREATED)

    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def buy_now(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))

    if not user_id:
        return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(Person, id=user_id)
        product = prodProduct.objects.get(productid=product_id)

        if product.productStock < quantity:
            return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        # Manually replicate get or create logic
        try:
            basket_item = Basket.objects.get(
                productid=product,
                Person_fk=user,
                is_checkout=False
            )
            # INCREMENT existing quantity rather than overwrite
            basket_item.productqty += quantity
        except Basket.DoesNotExist:
            basket_item = Basket(
                productid=product,
                Person_fk=user,
                is_checkout=False,
                productqty=quantity
            )

        basket_item.save()  # No force_insert, so custom Basket.save() won't cause an error
        return Response({'message': 'Product added for immediate purchase'}, status=status.HTTP_200_OK)

    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View a seller's products and sales analytics
@api_view(['GET'])
def view_seller(request, seller_id):
    try:
        # Get seller details
        seller = Person.objects.get(pk=seller_id)
        products = prodProduct.objects.filter(Person_fk=seller)
        analyticsfilter = Basket.objects.filter(productid__Person_fk=seller)

        # Calculate analytics
        total_sales = analyticsfilter.filter(
            Q(status="Order Received") | Q(status="Product Reviewed")
        ).aggregate(Sum('productqty'))['productqty__sum'] or 0

        # Fix distinct issue
        total_orders = analyticsfilter.values('transaction_code').annotate(
            transaction_count=Count('transaction_code')
        ).count()

        # Additional analytics
        gross_income_data = analyticsfilter.filter(
            Q(status="Order Received") | Q(status="Product Reviewed")
        ).annotate(
            gross_income=F('productid_id__productPrice') * F('productqty')
        ).aggregate(Sum('gross_income'))
        
        gross_income = gross_income_data.get('gross_income__sum', 0) or 0
        
        product_in_shop = products.count()

        most_popular_product = prodProduct.objects.filter(
            Person_fk=seller
        ).order_by('-productSold').first()

        most_popular_product_name = most_popular_product.productName if most_popular_product else "N/A"

        # Prepare response data
        seller_data = {
            'seller_name': seller.Username,
            'products': [
                {"productid": p.productid, "name": p.productName, "price": p.productPrice} 
                for p in products
            ],
            'total_sales': total_sales,
            'total_orders': total_orders,
            'gross_income': gross_income,
            'product_in_shop': product_in_shop,
            'most_popular_product': most_popular_product_name,
        }

        return Response(seller_data, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'Seller does not exist'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Example of updating a product (for seller)
@api_view(['PUT'])
def update_product(request, product_id):
    try:
        product = prodProduct.objects.get(productid=product_id)

        product.productName = request.data.get('product_name', product.productName)
        product.productDesc = request.data.get('product_desc', product.productDesc)
        product.productPrice = request.data.get('product_price', product.productPrice)
        product.productStock = request.data.get('product_stock', product.productStock)

        # If there's a new image, update it
        if 'product_photo' in request.FILES:
            product.productPhoto = request.FILES['product_photo']

        product.save()

        return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)

    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

# Example of deleting a product (for seller)
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = prodProduct.objects.get(productid=product_id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)

    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

# Endpoint to retrieve product reviews (if needed)
@api_view(['GET'])
def get_product_reviews(request, product_id):
    try:
        reviews = prodReview.objects.filter(productid_id=product_id)
        review_data = [{"review_text": r.review, "rating": r.rating} for r in reviews]
        return Response(review_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#endpoint to view sshop analytics 
def get_seller_analytics(request, pk):
    try:
        # Get seller
        seller = Person.objects.get(id=pk)
        analyticsfilter = Basket.objects.filter(productid_id__Person_fk=seller)

        # Gross Income
        gross_income_data = analyticsfilter.filter(
            Q(status="Order Received") | Q(status="Product Reviewed")
        ).annotate(
            gross_income=F('productid_id__productPrice') * F('productqty')
        ).aggregate(Sum('gross_income'))
        gross_income = gross_income_data.get('gross_income__sum', 0) or 0

        # Products Sold
        product_sold = analyticsfilter.filter(
            Q(status="Order Received") | Q(status="Product Reviewed")
        ).aggregate(Sum('productqty'))['productqty__sum'] or 0

        # Products in Shop
        product_in_shop = prodProduct.objects.filter(Person_fk=seller).count()

        # Most Popular Product
        most_popular_product = prodProduct.objects.filter(
            Person_fk=seller
        ).order_by('-productSold').first()
        
        most_popular_product_name = most_popular_product.productName if most_popular_product else "N/A"

        # Total Orders (Fix for distinct issue)
        total_orders = analyticsfilter.values('transaction_code').annotate(
            transaction_count=Count('transaction_code')
        ).count()

        # Pending Orders
        pending_order = analyticsfilter.filter(
            Q(status="Package Order") | Q(status="Payment Made")
        ).values('transaction_code').annotate(
            order_count=Count('transaction_code')
        ).count()

        # Shipped Orders
        shipped_order = analyticsfilter.filter(
            Q(status="Ship Order")
        ).values('transaction_code').annotate(
            order_count=Count('transaction_code')
        ).count()

        # Completed Orders
        completed_order = analyticsfilter.filter(
            Q(status="Order Received") | Q(status="Product Reviewed")
        ).values('transaction_code').annotate(
            order_count=Count('transaction_code')
        ).count()

        # Cancelled Orders
        cancelled_order = analyticsfilter.filter(
            Q(status="Cancel")
        ).values('transaction_code').annotate(
            order_count=Count('transaction_code')
        ).count()

        # Response Data
        data = {
            'gross_income': gross_income,
            'product_sold': product_sold,
            'product_in_shop': product_in_shop,
            'most_popular_product': most_popular_product_name,
            'total_order': total_orders,
            'pending_order': pending_order,
            'shipped_order': shipped_order,
            'completed_order': completed_order,
            'cancelled_order': cancelled_order
        }

        return JsonResponse(data)

    except Person.DoesNotExist:
        return JsonResponse({'error': 'Seller does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# Get products by seller ID
def get_products_by_seller(request, seller_id):
    try:
        products = prodProduct.objects.filter(Person_fk_id=seller_id)
        product_list = []

        for product in products:
            product_list.append({
                'productid': product.productid,
                'productName': product.productName,
                'productDesc': product.productDesc,
                'productPrice': product.productPrice,
                'productStock': product.productStock,
                # Return relative path for productPhoto
                'productPhoto': product.productPhoto.url if product.productPhoto else None,
                'timePosted': product.timePosted,
            })

        return JsonResponse({'products': product_list}, safe=False)
    except prodProduct.DoesNotExist:
        return JsonResponse({'error': 'No products found for this seller'}, status=404)

@api_view(['POST', 'GET'])
def sell_product(request, fk1):
    person = get_object_or_404(Person, pk=fk1)

    if request.method == 'POST':
        # Create a new product instance
        product = prodProduct()  # Create an instance of the prodProduct model

        # Product Name Validation
        product.productName = request.data.get('productName')
        if len(product.productName) > 30 or len(product.productName) == 0:
            return Response({'error': 'Product name cannot be empty and must be 30 characters or less.'}, status=status.HTTP_400_BAD_REQUEST)

        # Product Description Validation
        product.productDesc = request.data.get('productDesc')
        if len(product.productDesc) > 1500 or len(product.productDesc) == 0:
            return Response({'error': 'Product description cannot be empty and must be 1500 characters or less.'}, status=status.HTTP_400_BAD_REQUEST)

        # Product Category Validation
        product.productCategory = request.data.get('productCategory')
        custom_category = request.data.get('customCategory')
        if product.productCategory == "None Selected":
            return Response({'error': 'Product category must be selected.'}, status=status.HTTP_400_BAD_REQUEST)

        if product.productCategory == "Others" and custom_category:
            product.productCategory = custom_category
            if len(product.productCategory) == 0:
                return Response({'error': 'Custom product category cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Product Price Validation
        product.productPrice = request.data.get('productPrice')
        price_pattern = r'^\d+(\.\d{1,2})?$'
        if not re.match(price_pattern, str(product.productPrice)):
            return Response({'error': 'Invalid product price format. Use digits and allow up to two decimal places.'}, status=status.HTTP_400_BAD_REQUEST)

        # Product Stock Validation
        product.productStock = request.data.get('productStock')
        if len(product.productStock) == 0 or not product.productStock.isdigit():
            return Response({'error': 'Product stock must be a non-empty numeric value.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'productPhoto' in request.FILES:
            product.productPhoto = request.FILES['productPhoto']
        else:
            return Response({'error': 'Product photo cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set person and save the product
        product.Person_fk = person
        product.save()

        return Response({'message': 'Product created successfully.', 'productId': product.productid}, status=status.HTTP_201_CREATED)

    else:  # Handle GET request
        return Response({'person': person.id}, status=status.HTTP_200_OK)