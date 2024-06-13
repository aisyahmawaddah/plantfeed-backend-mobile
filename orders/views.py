from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from marketplace.models import prodProduct
from django.core.cache import cache
from basket.models import Basket
from .models import Person
from django.shortcuts import render, get_object_or_404
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
from basket.models import Basket, prodReview
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from orders.models import Order
from decimal import Decimal
from collections import defaultdict

import json
    
# def history(request):
#     try:
#         product=prodProduct.objects.all()
#         person=Person.objects.get(Email=request.session['Email'])
#         user=Person.objects.all()
#         allBasket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=1)
#         basketCount = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)
#         context = {
#             'allBasket': allBasket,
#             'basketCount': basketCount,
#             'product': product,
#             'person': person,
#             'user': user,
#         }
#         return render(request,'history.html', context)
#     except prodProduct.DoesNotExist:
#         raise Http404('Data does not exist')

def history(request):
    try:
        product=prodProduct.objects.all()
        person=Person.objects.get(Email=request.session['Email'])
        user=Person.objects.all()
        allBasket = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=1)
        basketCount = Basket.objects.all().filter(Person_fk_id=person.id,is_checkout=0)    
        
        context = {
            'allBasket': allBasket,
            'basketCount': basketCount,
            'product': product,
            'person': person,
            'user': user,
        }
        return render(request,'history.html', context)
    except prodProduct.DoesNotExist:
        raise Http404('Data does not exist')

# def cancel_order(request):
#     transaction_code = request.POST.get('transaction_code')

#     order_obj = Order.objects.get(transaction_code=transaction_code)
#     order_obj.status = "Cancel"
#     order_obj.save()
    
#     basket_obj = Basket.objects.filter(transaction_code=transaction_code)
#     basket_obj.update(status="Cancel")

#     return JsonResponse({'status': 1, 'message': 'status updated to Cancelled'})

def cancel_order(request, fk1, seller_id):
    ids = get_object_or_404(Basket, id=fk1)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    order = get_object_or_404(Order, transaction_code=ids.transaction_code)
    
    order.status = "Cancel"
    order.save()
    
    for basket_item in basket:
        # Update the product stock for each item in the basket
        product = basket_item.productid  # Access the prodProduct instance
        product.productStock += basket_item.productqty  # Update the stock
        product.save()  # Save the changes
    
    basket.update(status="Cancel")
    
    return redirect('orders:history')

def complete_order(request, fk1, seller_id):
    ids = get_object_or_404(Basket, id=fk1)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    order = get_object_or_404(Order, transaction_code=ids.transaction_code)
    
    order.status = "Order Received"
    order.save()
    
    basket.update(status="Order Received")
    
    return redirect('orders:history')

def review_product(request, fk1, seller_id):
    person = Person.objects.get(Email=request.session['Email'])
    ids = get_object_or_404(Basket, id=fk1)
    products = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    # product = get_object_or_404(prodProduct, pk=ids.productid.productid)
    print(products)
    
    if request.method == "POST":   
        for product in products:
            content = request.POST.get(f'review_{product.productid.productid}')
            print(content)
            if content:
                review = prodReview()
                review.content = content
                review.restricted = False
                review.Person_fk = Person.objects.get(Email=request.session['Email'])
                review.basketid = product
                review.productid = product.productid
                review.save()

        products.update(status="Product Reviewed")
        return redirect('orders:history')
    else:
        return render(request,'ReviewProduct.html', {'products':products, 'person':person, 'bas':ids})

# def complete_order(request):
#     transaction_code = request.POST.get('transaction_code')
#     # product=prodProduct.objects.all()
#     # product.productStock -= product.productqty
#     # product.save()
#     order_obj = Order.objects.get(transaction_code=transaction_code)
#     order_obj.status = "Order Received"
#     order_obj.save()
    
#     basket_obj = Basket.objects.filter(transaction_code=transaction_code)
#     basket_obj.update(status="Order Received")

#     return JsonResponse({'status': 1, 'message': 'status updated to Completed'})

# def invoice(request,fk1):
#     ids = Basket.objects.get(id=fk1)
#     product = prodProduct.objects.all()
#     basket = Basket.objects.all().filter(transaction_code=ids.transaction_code)
#     order = Order.objects.get(transaction_code=ids.transaction_code)
#     return render(request,'invoice.html',{'basket':basket,'order':order, 'product':product})

def invoice(request,fk1, seller_id):
    ids = get_object_or_404(Basket, id=fk1)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    order = get_object_or_404(Order, transaction_code=ids.transaction_code)
    
    total = sum((bas.productid.productPrice * bas.productqty for bas in basket))
    shipping = sum((bas.productqty * Decimal('5.00') for bas in basket))  # Shipping is RM5.00 per item
    
    final_total = total + shipping
    
    return render(request,'invoice.html',{'basket':basket,'order':order, 'shipping':shipping, 'final_total':final_total})

# def invoice(request, fk1):
#     try:
#         basket = Basket.objects.get(id=fk1)
#         seller_id = basket.productid.Person_fk_id
#         products = Basket.objects.filter(transaction_code=basket.transaction_code)
#         order = Order.objects.get(transaction_code=basket.transaction_code)

#         context = {
#             'products': products,
#             'order': order,
#         }

#         return render(request, 'invoice.html', context)
#     except Basket.DoesNotExist:
#         raise Http404('Basket does not exist')

def order_again(request, fk1, seller_id):
    ids = get_object_or_404(Basket, id=fk1)
    basket = Basket.objects.filter(transaction_code=ids.transaction_code, productid__Person_fk_id=seller_id)
    for item in basket:
        product = item.productid
        user = item.Person_fk
        productqty = item.productqty

        if product.productStock < productqty:
            messages.error(request, f'{product.productName}(s) exceeds the stock limit in your basket')
            return redirect('../../../MainMarketplace.html')

        basket = Basket.objects.filter(productid=product, Person_fk=user, is_checkout=0)

        if len(basket) > 0:
            basket = Basket.objects.get(Person_fk=user, productid=product, is_checkout=0)
            if basket.productqty + productqty > product.productStock:
                messages.error(request, f'{product.productName}(s) exceeds the stock limit in your basket')
                return redirect('../../../MainMarketplace.html')
            basket.productqty += productqty
            basket.save()

            messages.success(request, 'Previous order successfully added to your basket')
            return redirect('basket:summary',)
        else:
            basket = Basket(productqty=productqty, productid=product, Person_fk=user, is_checkout=0,
                            transaction_code='').save()

    return redirect('basket:summary',)

#SELLER's HISTORY
def SellHistory(request, fk1):
    person = Person.objects.get(Email=request.session['Email'])
    seller = Person.objects.get(pk=fk1)
    products = prodProduct.objects.filter(Person_fk=seller)
    product_ids = [product.productid for product in products]
    baskets = Basket.objects.filter(productid__in=product_ids, is_checkout=1)
    transactions = baskets.values_list('transaction_code', flat=True).distinct()
    orders = Order.objects.filter(transaction_code__in=transactions)

    products_by_order = {}
    for order in orders:
        product_baskets = Basket.objects.filter(transaction_code=order.transaction_code, productid__in=product_ids)
        products = []
        total_price_for_seller = Decimal('0.00')
        for product_basket in product_baskets:
            subtotal = product_basket.productid.productPrice * product_basket.productqty
            total_price_for_seller += subtotal
            products.append({
                "address": order.address,
                "total": order.total,
                "shipping": order.shipping,
                "productQty": product_basket.productqty,
                "productName": product_basket.productid.productName,
                "productDesc": product_basket.productid.productDesc,
                "productPrice": product_basket.productid.productPrice,
                "productCategory": product_basket.productid.productCategory,
                "orderStatus": order.status,
            })
        if products:  # Only add to the dictionary if there are products for this seller
            products_by_order[order.transaction_code] = {
                "transaction_code": order.transaction_code,
                "buyer_email": order.email,
                "buyer_name": order.name,
                "products": products,
                "total_price_for_seller": total_price_for_seller,
                "orderStatus": order.status
            }

    if products_by_order:
        return render(request, 'SellHistory.html', {'products_by_order': products_by_order, 'person':person})
    else:
        return render(request, 'SellHistory.html', {'message': 'No orders found. Start selling your items!', 'person':person})

def update_order_status(request):
    order_id = request.POST.get('order_id')
    order_status = request.POST.get('order_status')
    
    order_obj = Order.objects.get(transaction_code=order_id)
    order_obj.status = order_status
    order_obj.save()

    basket_objs = Basket.objects.filter(transaction_code=order_id)
    for basket_obj in basket_objs:
        basket_obj.status = order_status
        basket_obj.save()
    
    response = {'status': 1, 'message': 'Order status updated successfully'}
    
    return HttpResponse(json.dumps(response), content_type='application/json')