from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import prodProduct, Person
from basket.models import Basket, prodReview
from member.models import Person
from django.db.models import Sum, Q
from .serializers import ProductSerializer, ReviewSerializer
from django.http import JsonResponse
import re
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def list_products(request):
    products = prodProduct.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_product(request, product_id):
    try:
        product = prodProduct.objects.get(productid=product_id)
        reviews = prodReview.objects.filter(productid=product)

        serialized_reviews = ReviewSerializer(reviews, many=True).data

        product_data = {
            "productid": product.productid,
            "name": product.productName,
            "description": product.productDesc,
            "category": product.productCategory,
            "price": product.productPrice,
            "stock": product.productStock,
            "photo": product.productPhoto.url if product.productPhoto else None,
            "rating": product.productRating,
            "sold": product.productSold,
            "time_posted": product.timePosted.isoformat(),
            "restricted": product.restricted,
            "seller_info": {
                "id": product.Person_fk.id,
                "Username": product.Person_fk.Username,
                "Email": product.Person_fk.Email,
            },
            "reviews": serialized_reviews
        }

        return JsonResponse(product_data)  # Use JsonResponse which handles utf-8 encoding
    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    
# Add a product to the basket
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_to_basket(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    try:
        user = request.user  # This takes the token from the Authorization header
        product = prodProduct.objects.get(productid=product_id)

        if product.productStock < quantity:
            return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        basket_item, created = Basket.objects.get_or_create(productid=product, Person_fk=user, is_checkout=False)
        if not created:
            basket_item.productqty += quantity
        else:
            basket_item.productqty = quantity
        basket_item.save()

        return Response({'message': 'Product added to basket'}, status=status.HTTP_201_CREATED)
    except prodProduct.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Buy now functionality
@api_view(['POST'])
def buy_now(request):
    user_email = request.data.get('email')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    try:
        user = Person.objects.get(Email=user_email)
        product = prodProduct.objects.get(productid=product_id)
        
        if product.productStock < quantity:
            return Response({'error': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        basket_item, created = Basket.objects.get_or_create(productid=product, Person_fk=user, is_checkout=0)
        basket_item.productqty = quantity
        basket_item.save()

        # Additional logic for immediate checkout can be placed here
        return Response({'message': 'Product added for immediate purchase'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View a seller's products and sales analytics
@api_view(['GET'])
def view_seller(request, seller_id):
    try:
        seller = Person.objects.get(pk=seller_id)
        products = prodProduct.objects.filter(Person_fk=seller)

        analyticsfilter = Basket.objects.filter(productid__Person_fk=seller)
        
        # Calculate analytics
        total_sales = analyticsfilter.filter(Q(status="Order Received") | Q(status="Product Reviewed")) \
                                     .aggregate(Sum('productqty'))['productqty__sum'] or 0
        
        total_orders = analyticsfilter.distinct('transaction_code').count()
        
        # Prepare response data
        seller_data = {
            'seller_name': seller.Username,
            'products': [{"productid": p.productid, "name": p.productName, "price": p.productPrice} for p in products],
            'total_sales': total_sales,
            'total_orders': total_orders,
        }

        return Response(seller_data, status=status.HTTP_200_OK)

    except Person.DoesNotExist:
        return Response({'error': 'Seller does not exist'}, status=status.HTTP_404_NOT_FOUND)

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