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
