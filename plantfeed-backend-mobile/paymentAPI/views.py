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

# Using Django
from django.http import HttpResponse

class ProductLandingPageView(TemplateView):
    template_name = 'checkout-test.html'
    def get_context_data(self, **kwargs):
        basket_ids = [4, 2]  # List of product IDs you want to fetch
        basket = Basket.objects.filter(id__in=basket_ids)
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            'basket': basket,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        })
        return context
    
class SuccessPageView(TemplateView):
    template_name = 'success.html'
    
class CancelPageView(TemplateView):
    template_name = 'cancel.html'
    
    def cancel_page(request):
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
        
# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         selected_product_ids = request.POST.getlist('selected_products')
#         selected_products = Basket.objects.all().filter(id__in=selected_product_ids)

#         line_items = []
        
#         for product in selected_products:
#             line_item = {
#                 'price_data': {
#                     'currency': 'myr',
#                     'unit_amount': int(product.productid.productPrice * 100),
#                     'product_data': {
#                         'name': product.productid.productName,
#                         'description': product.productid.productDescription,
#                     },
#                 },
#                 'quantity': product.productqty,
#             }
#             line_items.append(line_item)

#         YOUR_DOMAIN = "http://127.0.0.1:8000/paymentAPI"
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items= line_items,
#             metadata={'productid': productId},
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/success/',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#         )
#         return JsonResponse({
#             'id': checkout_session.id
#         })
        
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('selected_products')
        products = Basket.objects.all().filter(id__in=product_ids)
        YOUR_DOMAIN = "http://127.0.0.1:8000/paymentAPI"

        line_items = []
        for product in products:
            line_items.append({
                'price_data': {
                    'currency': 'myr',
                    'unit_amount': int(product.productid.productPrice * 100),
                    'product_data': {
                        'name': product.productid.productName,
                    },
                },
                'quantity': 1,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )

        return JsonResponse({
            'id': checkout_session.id
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         productId = self.kwargs['pk1']
#         prod = prodProduct.objects.get(productid = productId)
#         stripePrice = int(prod.productPrice * 100)
#         YOUR_DOMAIN = "http://127.0.0.1:8000/paymentAPI"
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'myr',
#                         'unit_amount': stripePrice,
#                         'product_data': {
#                             'name': prod.productName,
#                         },
#                     },
#                     'quantity': 2,
#                 },
#             ],
#             metadata={'productid': productId},
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/success/',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#         )
#         return JsonResponse({
#             'id': checkout_session.id
#         })

# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         # Retrieve product IDs from request (e.g., list of product IDs)
#         product_ids = request.POST.getlist('product_ids', [])  # Assuming product_ids is passed as a list in the POST data

#         # Retrieve product information for the selected product IDs
#         line_items = []
#         total_amount = 0
        
#         for product_id in product_ids:
#             product = prodProduct.objects.get(productid=product_id)
#             stripe_price = int(product.productPrice * 100)
            
#             # Create a line item for each product
#             line_item = {
#                 'price_data': {
#                     'currency': 'myr',
#                     'unit_amount': stripe_price,
#                     'product_data': {
#                         'name': product.productName,
#                     },
#                 },
#                 'quantity': 1,  # You can adjust the quantity as needed
#             }
            
#             line_items.append(line_item)
#             total_amount += stripe_price  # Calculate total amount for all line items

#         # Define your domain (replace with your actual domain)
#         YOUR_DOMAIN = "http://127.0.0.1:8000/paymentAPI"

#         # Create a Stripe Checkout Session with multiple line items
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=line_items,
#             metadata={'product_ids': product_ids},  # Optionally pass metadata
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/success/',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#         )

#         # Return the Checkout Session ID as a JSON response
#         return JsonResponse({'id': checkout_session.id, 'total_amount': total_amount})

def stripe_webhook(request):
    payload = request.body
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
    )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
        event['data']['object']['id'],
        expand=['line_items'],
        )
        
        customer_email = session["customer_details"]["email"]
        productid = session["metadata"]["productid"]
        prod = prodProduct.objects.get(productid = productid)
        
        
        send_mail(
            subject='Order Confirmation',
            message=f"Thank you for your order. Your order has been successfully placed.",
            recipient_list=[customer_email],
            from_email=settings.EMAIL_HOST_USER
        )
        
        # TODO - decide whether you want to send the file or URL to the user

        line_items = session.line_items
        # Fulfill the purchase...
        fulfill_order(line_items)

    # Passed signature verification
    return HttpResponse(status=200)

def fulfill_order(line_items):
  # fill me in
  print("Fulfilling order")