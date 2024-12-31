from decimal import Decimal
from django.db import models, migrations
from django.conf import settings
from datetime import datetime
from marketplace.models import prodProduct
from member.models import Person

class Basket(models.Model):

    class Meta:
        db_table = 'basket'
    productqty = models.IntegerField(default=0)
    productid = models.ForeignKey(prodProduct, on_delete=models.CASCADE)
    Person_fk = models.ForeignKey(Person, on_delete=models.CASCADE)
    is_checkout = models.BooleanField(default=0)
    transaction_code = models.CharField(max_length=255,null=True)
    status = models.CharField(max_length=250,null=True)
    
    def save(self):
        super().save()
        
class prodReview(models.Model):
    
    class Meta:
        db_table = 'prodReview'
    content = models.CharField(max_length=1500,blank=True)
    restricted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    productid = models.ForeignKey(prodProduct, on_delete=models.CASCADE)
    Person_fk = models.ForeignKey(Person, on_delete=models.CASCADE)
    basketid = models.ForeignKey(Basket, on_delete=models.CASCADE)
    
    def save(self):
        super().save()
        
    def deleteReview(self):
        super().delete()
