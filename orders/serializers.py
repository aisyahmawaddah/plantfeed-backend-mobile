from rest_framework import serializers
from .models import Order, OrderItem
from basket.serializers import ProdProductSerializer, PersonSerializer
from basket.models import prodProduct 
from member.models import Person


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'Username', 'Email', 'Name']# Ensure these fields exist in your Person model

class ProdProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller_info.FullName', read_only=True)  # Assuming FullName is the correct field

    class Meta:
        model = prodProduct
        fields = ['productid', 'productName', 'productDesc', 'productCategory', 'productPrice', 
                  'productStock', 'productPhoto', 'productRating', 'productSold', 
                  'timePosted', 'restricted', 'seller_info']
        

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'name', 'email', 'address', 'shipping', 'transaction_code', 'total', 'status', 'user', 'items']