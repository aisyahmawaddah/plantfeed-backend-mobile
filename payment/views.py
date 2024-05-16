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
from marketplace.models import prodProduct
from basket.models import Basket
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.utils import timezone
from orders.models import Order
from django.shortcuts import render

# Create your views here.
# STRIPE Implementation Try 1
from django.http import JsonResponse
import stripe
from django.shortcuts import redirect
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from marketplace.models import prodProduct
from orders.models import Order
from member.models import Person
from django.http.response import Http404
from basket.models import Basket
# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.views.decorators.csrf import csrf_exempt

import json
import os
# from .models import Person

# Create your views here.
# def pay(request):
#     try:
#         tcode = 'TRANS#' + str(timezone.now())
#         orderStatus = "Payment Made"
#         person = Person.objects.get(Email=request.session['Email'])

#         # Retrieve all basket items for the current user that are not checked out
#         basket_items = Basket.objects.filter(Person_fk_id=person.id, is_checkout=0)

#         # Dictionary to store total amount for each seller
#         seller_totals = {}

#         # Calculate total amount for each seller
#         for bas in basket_items:
#             seller_id = bas.productid.Person_fk_id
#             if seller_id not in seller_totals:
#                 seller_totals[seller_id] = 0

#             seller_totals[seller_id] += bas.productid.productPrice * bas.productqty

#         # Process each seller's items and create a single order for each seller
#         for seller_id, total in seller_totals.items():
#             # Create a single order for this seller
#             ord = Order()
#             ord.name = request.POST['name']
#             ord.email = request.POST['email']
#             ord.address = request.POST['address']
#             ord.payment = request.POST['payment']
#             ord.creditnumber = request.POST['creditnumber']
#             ord.expiration = request.POST['expiration']
#             ord.cvv = request.POST['cvv']
#             ord.transaction_code = tcode
#             ord.user_id = person.id
#             ord.namecard = request.POST['namecard']
#             ord.shipping = request.POST['shipping']
#             ord.total = total
#             ord.status = orderStatus
#             ord.seller_id = seller_id
#             ord.save()

#         # Mark all basket items as checked out
#         basket_items.update(is_checkout=1, transaction_code=tcode, status=orderStatus)

#         return redirect('orders:history')

#     except Person.DoesNotExist:
#         raise Http404('User does not exist')

def pay(request):
    tcode = 'TRANS#'+str(timezone.now())
    orderStatus = "Payment Made"
    person=Person.objects.get(Email=request.session['Email'])
    
    for bas in Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0) :
        prod = prodProduct.objects.all().get(productid=bas.productid.productid)
        prod.productStock -= bas.productqty
        if prod.productStock < 0 :
            return HttpResponse('Stock is not enough', content_type='application/json')
        else :
            prod.save()
    ord = Order()
    ord.name = request.POST['name']
    ord.email = request.POST['email']
    ord.address = request.POST['address']
    ord.payment = request.POST['payment']
    ord.creditnumber = request.POST['creditnumber']
    ord.expiration = request.POST['expiration']
    ord.cvv = request.POST['cvv']
    ord.transaction_code = tcode
    ord.user_id = person.id
    ord.namecard = request.POST['namecard']
    ord.shipping = request.POST['shipping']
    ord.total = request.POST['total']
    ord.status = orderStatus

    ord.save()
    Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0).update(is_checkout=1,transaction_code=tcode, status = orderStatus)
    return redirect('orders:history')

def checkoutSession(request):
    if request.method == 'POST':
        person=Person.objects.get(Email=request.session['Email'])
        selected_product_ids = request.POST.getlist('selected_products')
        selected_products = Basket.objects.all().filter(id__in=selected_product_ids)
        YOUR_DOMAIN = "http://127.0.0.1:8000/payment"     
        
        line_items = []
        
        for product in selected_products:
            description = product.productid.productDesc if product.productid.productDesc else "No description available"
            line_items.append({
                'price_data': {
                    'currency': 'myr',
                    'unit_amount': int((product.productid.productPrice + 2) * 100),
                    'product_data': {
                        'name': product.productid.productName,
                        'description': description,
                    },
                },
                'quantity': product.productqty,
            })
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=person.Email,
            submit_type='pay',
            shipping_address_collection={
              'allowed_countries': ['MY', 'SG', 'ID', 'TH', 'BN'],
            },
            payment_method_types=['card'],
            line_items=line_items,
            # metadata={'selected_products': str(selected_product_ids)},  # convert to string if needed
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id,
        })
        
    return JsonResponse({'error': 'Invalid request'}, status=400)
        
# def create_checkout_session(request):
#     if request.method == 'POST':
#         product_ids = request.POST.getlist('selected_products')
#         products = Basket.objects.all().filter(id__in=product_ids)
#         YOUR_DOMAIN = "http://127.0.0.1:8000/paymentAPI"

#         line_items = []
#         for product in products:
#             line_items.append({
#                 'price_data': {
#                     'currency': 'myr',
#                     'unit_amount': int(product.productid.productPrice * 100),
#                     'product_data': {
#                         'name': product.productid.productName,
#                     },
#                 },
#                 'quantity': 1,
#             })

#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=line_items,
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/success/',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#         )

#         return JsonResponse({
#             'id': checkout_session.id
#         })

#     return JsonResponse({'error': 'Invalid request'}, status=400)
        
def successCheckout(request):
    return render(request,'success.html')  
   
def cancelCheckout(request):
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
