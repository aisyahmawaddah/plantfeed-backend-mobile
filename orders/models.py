from decimal import Decimal
from django.conf import settings
from django.db import models
from member.models import Person

from marketplace.models import prodProduct


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    class Meta:
        db_table = 'Order'
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    shipping = models.CharField(max_length=1000, null=True)
    transaction_code = models.CharField(max_length=1000)
    total = models.FloatField(null=True)
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default='Pending')
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(prodProduct, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)