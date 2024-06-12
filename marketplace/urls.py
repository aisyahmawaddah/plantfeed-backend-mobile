from django.contrib import admin
from django.urls import path
from django.urls import re_path as url, include
# from LOGIN import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from LOGIN.views import UserReg, sharing, discussion, view, workshop, booking, member
from .import views
# from .import index
from .views import *
# from .api import UserList, UserDetail, UserAuthentication

app_name = 'marketplace'
urlpatterns = [
    path('MainMarketplace',views.mainMarketplace, name="MainMarketplace"),
    path('SellProduct.html/<str:fk1>/',views.sellProduct, name="SellProduct"),
    path('DeleteProduct/<str:fk1>/',views.deleteProduct, name="DeleteProduct"),
    path('UpdateProduct.html/<str:fk1>/',views.updateProduct, name="UpdateProduct"),
    path('MyMarketplace',views.myMarketplace, name="MyMarketplace"),
    path('buy_now/<str:fk1>/<str:fk2>/',views.buy_now, name='buy_now'),
    path('add_to_basket/<str:fk1>/<str:fk2>/',views.add_to_basket, name='add_to_basket'),
    path('ViewProduct/<str:pk>',views.viewProduct, name="viewProduct"),
    path('ViewSeller/<str:pk>',views.viewSeller, name="viewSeller"),
    path('RestrictProduct/<str:fk1>/',views.restrictProduct, name="restrictProduct"),
    path('UnrestrictProduct/<str:fk1>/',views.unrestrictProduct, name="unrestrictProduct")

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()