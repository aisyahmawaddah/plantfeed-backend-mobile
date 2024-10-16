# from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from marketplace.models import prodProduct
from django.core.cache import cache
from basket.models import Basket
from .models import Person
from django.shortcuts import render
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
# from LOGIN.models import Person as FarmingPerson
# from LOGIN.models import Feed, Booking, Workshop, Group, Member 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
# from .forms import CreateInDiscussion, PersonForm, UserUpdateForm
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
from member.models import Person
# from sharing.models import Feed
from .models import prodProduct
from basket.models import Basket
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from decimal import Decimal
from django.conf import settings

import json
import os

def checkout(request):
    product=prodProduct.objects.all()
    person=Person.objects.get(Email=request.session['Email'])
    basket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
    selected_product_ids = request.POST.getlist('selected_products')
    selected_products = Basket.objects.all().filter(id__in=selected_product_ids)
        
    # Initialize an empty dictionary to store subtotals
    subtotals = {}
    sellers = {}
    uniqueSellers = set()
    sellerTotal = {}

    # Calculate the subtotal for each product and store it in the dictionary
    for bas in selected_products:
        seller = bas.productid.Person_fk_id
        if seller not in uniqueSellers:
            uniqueSellers.add(seller)
            sellers[bas.id] = seller
            print(sellers[bas.id])
            
            # Initialize the total for the seller
            sellerTotal[seller] = 0
        
        # Calculate subtotal for the product
        subtotal = bas.productid.productPrice * bas.productqty + (5*bas.productqty)
        
        # Accumulate subtotal for the seller
        sellerTotal[seller] += subtotal
        
        subtotals[bas.id] = subtotal
        print(subtotals[bas.id])
        
        totalCheckout = sum(sellerTotal[seller] for seller in uniqueSellers)
        print(totalCheckout)

    return render(request, 'checkout.html', {'totalCheckout': totalCheckout, 'selected_products': selected_products, 'basket': basket, 'person': person, 'product': product, 'subtotals': subtotals, 'sellers': sellers, 'sellerTotal': sellerTotal, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})

def checkoutAll(request):
    product=prodProduct.objects.all()
    person=Person.objects.get(Email=request.session['Email'])
    selected_products = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
    basket = selected_products
    
    # Initialize an empty dictionary to store subtotals
    subtotals = {}
    sellers = {}
    uniqueSellers = set()
    sellerTotal = {}

    # Calculate the subtotal for each product and store it in the dictionary
    for bas in selected_products:
        seller = bas.productid.Person_fk_id
        if seller not in uniqueSellers:
            uniqueSellers.add(seller)
            sellers[bas.id] = seller
            print(sellers[bas.id])
            
            # Initialize the total for the seller
            sellerTotal[seller] = 0
        
        # Calculate subtotal for the product
        subtotal = bas.productid.productPrice * bas.productqty + (5*bas.productqty)
        
        # Accumulate subtotal for the seller
        sellerTotal[seller] += subtotal
        
        subtotals[bas.id] = subtotal
        print(subtotals[bas.id])
        
        print(sellerTotal[seller])
        
        totalCheckout = sum(sellerTotal[seller] for seller in uniqueSellers)
        print(totalCheckout)
        
    print(selected_products)
    return render(request, 'checkout.html', {'totalCheckout': totalCheckout, 'subtotals': subtotals, 'basket': basket, 'selected_products':selected_products, 'person': person, 'product': product, 'sellers': sellers, 'sellerTotal': sellerTotal, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})

def summary(request):
    try:
        product=prodProduct.objects.all()
        person=Person.objects.get(Email=request.session['Email'])
        user=Person.objects.all()
        allBasket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
        
        total = 0
        
        for x in allBasket:
            total += x.productid.productPrice * x.productqty
        context = {
            'allBasket': allBasket,
            'product': product,
            'person': person,
            'user': user,
            'total':total
        }
        return render(request,'summary.html', context)
    except prodProduct.DoesNotExist:
        raise Http404('Data does not exist')

def remove_basket_qty(request):
    request.POST['item_id']
    obj = Basket.objects.get(id=request.POST['item_id'])
    if obj.productqty > 1:
        obj.productqty -= 1
        obj.save()
    else :
        obj.delete()

    response = {'status':1,'message':'ok'}
    return HttpResponse(json.dumps(response),content_type='application/json')

def add_basket_qty(request):
    request.POST['item_id']
    basket_obj = Basket.objects.get(id=request.POST['item_id'])
    prod_obj = prodProduct.objects.get(productid=basket_obj.productid.productid)
    
    if prod_obj.productStock > basket_obj.productqty:
        basket_obj.productqty += 1
        basket_obj.save()
        response = {'status':1,'message':'ok'}
    else:
        response = {'status':0,'message':'Not enough stock for this product'}

    return HttpResponse(json.dumps(response),content_type='application/json')

def basket_delete(request):
    request.POST['item_id']
    obj = Basket.objects.get(id=request.POST['item_id'])
    obj.delete()
    response = {'status':1,'message':'ok'}
    return HttpResponse(json.dumps(response),content_type='application/json')


    

