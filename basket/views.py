from django.http import JsonResponse
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

    

