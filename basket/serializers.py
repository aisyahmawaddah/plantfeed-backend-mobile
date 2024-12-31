from rest_framework import serializers
from .models import Basket, prodReview
from marketplace.models import prodProduct
from member.models import Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'Username', 'Email', 'Name']  # Ensure these fields exist in your Person model

class ProdProductSerializer(serializers.ModelSerializer):
    seller_info = PersonSerializer(source='Person_fk', read_only=True)  # Access the seller's information

    class Meta:
        model = prodProduct
        fields = [
            'productid', 'productName', 'productDesc', 'productCategory',
            'productPrice', 'productStock', 'productPhoto', 
            'productRating', 'productSold', 'timePosted', 
            'restricted', 'seller_info'  # Include seller info here
        ]

class BasketSerializer(serializers.ModelSerializer):
    productid = ProdProductSerializer(read_only=True)  # Nested product details that include seller info
    buyer_info = PersonSerializer(source='Person_fk', read_only=True)  # Buyer information

    class Meta:
        model = Basket
        fields = [
            'id', 'productqty', 'productid', 'buyer_info',  # Now includes buyer_info
            'is_checkout', 'transaction_code', 'status'
        ]

    def create(self, validated_data):
        # Handle the creation of related fields
        product_data = validated_data.pop('productid', None)
        person_data = validated_data.pop('buyer_info', None)
        basket_item = Basket.objects.create(**validated_data)
        return basket_item

    def update(self, instance, validated_data):
        instance.productqty = validated_data.get('productqty', instance.productqty)
        instance.is_checkout = validated_data.get('is_checkout', instance.is_checkout)
        instance.transaction_code = validated_data.get('transaction_code', instance.transaction_code)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def validate_productqty(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

class ProdReviewSerializer(serializers.ModelSerializer):
    productid = ProdProductSerializer(read_only=True)
    buyer_info = PersonSerializer(read_only=True)
    basketid = BasketSerializer(read_only=True)

    class Meta:
        model = prodReview
        fields = [
            'id', 'content', 'restricted', 'date',
            'productid', 'buyer_info', 'basketid'  # Ensure products and corresponding buyers are represented
        ]

    def create(self, validated_data):
        return super().create(validated_data)  # Use super for flexibility

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.restricted = validated_data.get('restricted', instance.restricted)
        instance.save()
        return instance