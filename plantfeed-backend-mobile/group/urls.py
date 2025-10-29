from django.contrib import admin
from django.urls import path
#from django.conf.urls import url, include
# from LOGIN import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from LOGIN.views import UserReg, sharing, discussion, view, workshop, booking, member
from .import views
#from django.conf.urls import url
from .views import *

# from .api import UserList, UserDetail, UserAuthentication

app_name = 'group'
urlpatterns = [
    path('MainGroup',views.mainGroup, name="MainGroup"),
    path('AddGroup',views.AddGroup, name="AddGroup"),
    path('MyGroup',views.myGroup, name="MyGroup"),
    path('ViewGroup/<str:pk>',views.viewGroup, name="ViewGroup"),
    path('JoinGroup/<str:pk>',views.joinGroup, name="JoinGroup"),
    path('DeleteGroup/<str:pk>',views.deleteGroup, name="DeleteGroup"),
    path('UpdateGroup/<str:pk>',views.updateGroup, name="UpdateGroup"),
    path('AddGroupSharing/<str:pk>',views.AddGroupSharing, name="AddGroupSharing"),
    path('Filter_SoilTag',views.Group_SoilTag, name="Group_SoilTag"),
    path('Filter_PlantTag',views.Group_PlantTag, name="Group_PlantTag"),
    path('GroupSharingComment/<str:pk>',views.addGSComment, name="GroupSharingComment"),
    path('PL-Sharing/<str:pk>', views.PLSharing, name="PL-Sharing"),
    path('PlantLink-Graph-API', views.PLGraphAPI, name="PlantLink-Graph-API"),
 

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()







