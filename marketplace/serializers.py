from rest_framework import serializers
from .models import prodProduct
from basket.models import Basket, prodReview  # Assuming prodReview is in basket.models
from member.models import Person


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'Username', 'Email', 'Photo']  # Expand or adjust as needed.

class ProductSerializer(serializers.ModelSerializer):
    seller_info = PersonSerializer(source='Person_fk', read_only=True)  # Adjust source for the serializer
    
    class Meta:
        model = prodProduct
        fields = [
            'productid', 'productName', 'productDesc', 'productCategory',
            'productPrice', 'productStock', 'productPhoto', 'productRating',
            'productSold', 'timePosted', 'restricted', 'seller_info'  # Include seller_info correctly
        ]

# Ensure BasketSerializer includes all relevant fields from Basket and product details
class BasketSerializer(serializers.ModelSerializer):
    productid = ProductSerializer(read_only=True)  # Nested product details include seller
    Person_fk = PersonSerializer(read_only=True)  # Buyer information

    class Meta:
        model = Basket
        fields = [
            'id', 'productqty', 'productid', 'Person_fk', 
            'is_checkout', 'transaction_code', 'status'
        ]

class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'Username', 'Email', 'Photo']  # Ensure these fields exist

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = ReviewerSerializer(source='Person_fk', read_only=True)

    class Meta:
        model = prodReview
        fields = [
            'id',              # Review ID
            'content',         # Review content
            'restricted',      # Restricted status
            'basketid_id',     # Foreign Key to Basket (ID)
            'productid_id',    # Foreign Key to Product (ID)
            'date',            # Date of review creation
            'reviewer'         # Include reviewer details
        ]

class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class SellerAnalyticsSerializer(serializers.Serializer):
    seller_name = serializers.CharField()
    products = ProductSerializer(many=True)
    total_sales = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    gross_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_in_shop = serializers.IntegerField()
    most_popular_product = serializers.CharField()
