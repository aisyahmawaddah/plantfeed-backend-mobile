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

# def BasketView(request, fk1):
#     product=prodProduct.objects.all()
#     allBasket=Basket.objects.all()
#     person=Person.objects.filter(Email=request.session['Email'])
#     user=Person.objects.all()
#     basket = Basket(request)
#     total = str(basket.get_total_price(fk1))
#     total = total.replace('.', '')
#     total = int(total)

#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     intent = stripe.PaymentIntent.create(
#         amount=total,
#         currency='myr',
#         metadata={'userid': request.user.id}
#     )

#     return render(request, 'payment/Payment.html', {'client_secret': intent.client_secret, 'basket':allBasket, 'product':product, 'person':person, 'user':user,
#                                                             'STRIPE_PUBLISHABLE_KEY': os.environ.get('STRIPE_PUBLISHABLE_KEY')})

# def summary(request):
#     try:
#         if 'Email' not in request.session:
#             # Redirect the user to the login page or handle the case when the user is not logged in
#             return redirect('login')

#         person = Person.objects.get(Email=request.session['Email'])
#         allBasket = Basket.objects.filter(Person_fk=person, is_checkout=False)

#         seller_products = {}

#         for basket_item in allBasket:
#             product = basket_item.productid
#             seller_name = product.Person_fk.Username

#             # Calculate subtotal for each product
#             subtotal = product.productPrice * basket_item.productqty
            
#             # Check if the product quantity exceeds the available stock
#             if basket_item.productqty > product.productStock:
#                 # Set a flag indicating that the checkout should be disabled for this product
#                 basket_item.disable_checkout = True
#                 basket_item.save()
#                 # Add an error message or take appropriate action to inform the user
            
#             # Initialize seller data if not already present
#             if seller_name not in seller_products:
#                 seller_products[seller_name] = {'products': [], 'subtotal': 0}

#             # Append product to the seller's products list
#             seller_products[seller_name]['products'].append(basket_item)
#             # Update the subtotal for the seller
#             seller_products[seller_name]['subtotal'] += subtotal

#         context = {
#             'person': person,
#             'allBasket': allBasket,
#             'seller_products': seller_products,
#         }
#         return render(request, 'summary.html', context)
#     except Person.DoesNotExist:
#         raise Http404('User does not exist')

#09/05/2024
# def checkout(request):
#     product=prodProduct.objects.all()
#     person=Person.objects.get(Email=request.session['Email'])
#     basket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
#     selected_product_ids = request.POST.getlist('selected_products')
#     selected_products = prodProduct.objects.filter(productid__in=selected_product_ids)
#     subtotal = sum(product.productPrice * basket.filter(productid=product).first().productqty for product in selected_products)
#     total_price = sum(product.productPrice for product in selected_products)
#     # print(selected_products)
#     return render(request, 'checkout.html', {'selected_products': selected_products, 'total_price': total_price, 'subtotal': subtotal, 'basket': basket, 'person': person, 'product': product})
#09/05/2024

#09/05/2024
def checkout(request):
    product=prodProduct.objects.all()
    person=Person.objects.get(Email=request.session['Email'])
    basket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
    selected_product_ids = request.POST.getlist('selected_products')
    selected_products = Basket.objects.all().filter(id__in=selected_product_ids)
    
    # for x in selected_products:
    #     subtotal = x.productid.productPrice * x.productqty
    #     print(subtotal)
        
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
        
    # subtotal = sum(selected_products.productid.productPrice * basket.filter(productid=product).first().productqty for product in selected_products)
    # total_price = sum(product.productPrice for product in selected_products)
    # subtotal = "Test"
    # print(selected_products)
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
        
    # subtotal = sum(product.productPrice * selected_products.productqty)
    # total_price = sum(product.productPrice)
    # subtotal = "Test"
    print(selected_products)
    return render(request, 'checkout.html', {'totalCheckout': totalCheckout, 'subtotals': subtotals, 'basket': basket, 'selected_products':selected_products, 'person': person, 'product': product, 'sellers': sellers, 'sellerTotal': sellerTotal, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})

#09/05/2024



#10/05/2024
# from collections import defaultdict

# def checkout(request):
#     person = Person.objects.get(Email=request.session['Email'])
#     basket = Basket.objects.filter(Person_fk=person, is_checkout=0)
    
#     selected_product_ids = request.POST.getlist('selected_products')
#     selected_products = prodProduct.objects.filter(productid__in=selected_product_ids)
    
#     # Create a dictionary to organize products by seller
#     products_by_seller = defaultdict(list)
#     for product in selected_products:
#         seller = product.Person_fk
#         products_by_seller[seller].append(product)
    
#     # Calculate subtotal for each product and total price for each seller
#     for seller, products in products_by_seller.items():
#         seller.total_price = sum(product.productPrice * basket.filter(productid=product).first().productqty for product in products)
#         for product in products:
#             product.subtotal = product.productPrice * basket.filter(productid=product).first().productqty
    
#     # Calculate total price including shipping for each seller
#     shipping_fee = Decimal('5.00')
#     for seller, products in products_by_seller.items():
#         seller.total_price_with_shipping = seller.total_price + shipping_fee
    
#     return render(request, 'checkout.html', {
#         'products_by_seller': products_by_seller,
#         'person': person,
#         'basket': basket,
#         'selected_products': selected_products
#     })
#10/05/2024

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

    

