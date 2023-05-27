from member import views
from sharing import views
from group import views
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', views.index ),
    path('', include('member.urls')),
    path('sharing/', include('sharing.urls')),
    path('group/', include('group.urls')),
    path('workshop/', include('workshop.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('basket/', include('basket.urls')),
    #path('api-auth/', include('rest_framework.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
