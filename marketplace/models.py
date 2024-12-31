from django.db import models
from decimal import Decimal
from django.db import models, migrations
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.syndication.views import Feed
from django.shortcuts import render
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from member.models import Person
    
class prodProduct(models.Model):
    class Meta:
        db_table = 'prodProduct'
    productid = models.AutoField(primary_key=True)
    productName = models.CharField(max_length=255, blank=True)
    productDesc = models.CharField(max_length=1500,blank=True)
    productCategory = models.CharField(max_length=255, blank=True)
    productPrice = models.DecimalField(max_digits=20, decimal_places=2)
    productStock = models.IntegerField(default=0)
    productPhoto = models.ImageField(upload_to ='images/', null=True)
    productRating = models.IntegerField(default=0)
    productSold = models.IntegerField(default=0)
    timePosted = models.DateTimeField(default=datetime.now, blank=True)
    Person_fk = models.ForeignKey(Person, on_delete=models.CASCADE)
    restricted = models.BooleanField(default=False)
    
    def save(self):
        super().save()
        return self.productid
    
    def deleteProduct(self):
        super().delete()

