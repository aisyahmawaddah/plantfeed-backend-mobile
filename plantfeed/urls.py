from member import views
from sharing import views
from group import views
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', views.index ),
    path('', include('member.urls')),
    path('sharing/', include('sharing.urls')),
    path('group/', include('group.urls')),
    path('workshop/', include('workshop.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('suggestion/', include('suggestion.urls')),
    path('basket/', include('basket.urls')),
    path('topic/', include('topic.urls')),
    path('payment/', include('payment.urls')),
    path('orders/', include('orders.urls')),
    path('paymentAPI/', include('paymentAPI.urls')),
    #path('api-auth/', include('rest_framework.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('plantlink/Login/', views.authenticate_user, name='authenticate_user'),
]
