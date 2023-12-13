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
from .import api

# from .api import UserList, UserDetail, UserAuthentication

app_name = 'sharing'
urlpatterns = [
    #path('MainSharing',views.mainSharing, name="MainSharing"),
    #path('SharingGroup/<str:pk>',views.sharingGroup, name="SharingGroup"),
    path('UpdateSharing/<str:pk>',views.updateSharing, name="UpdateSharing"),
    path('DeleteSharing/<str:pk>', views.deleteSharing, name="DeleteSharing"),
    path('Forum/<str:pk>', views.viewForum, name="Forum"),
    path('MainSharing',views.mainSharing, name="MainSharing"),
    path('AddNewSharing',views.AddSharing, name="AddSharing"),
    
    #path(',../MainPageSharing.html/<str:pk>', views.addLikes, name="AddLikes"),
    path('AddComment/<str:pk>', views.addComment, name="AddComment"),
    path('UpdateComment/<str:pk>',views.updateComment, name="UpdateComment"),
    path('DeleteComment/<str:pk>', views.deleteComment, name="DeleteComment"),
    path('AddLikes/<str:pk>', views.AddLikes, name="AddLikes"),
    

    path('MainSharing/Sharing_SoilTag',views.Sharing_SoilTag, name="Sharing_SoilTag"),
    path('MainSharing/Sharing_PlantTag',views.Sharing_PlantTag, name="Sharing_PlantTag"),
    # path('Sharing_PlantTag',views.Sharing_GeneralPlantTag, name="Sharing_GeneralPlantTag"),
    # path('Sharing_PlantTag/<str:plantTag>',views.Sharing_PlantTag, name="Sharing_PlantTag"),
    path('users/post-feed/', api.postFeed),
    path('users/feed/<int:creator_id>/', api.CreatorFeedView.as_view(), name='creator_feed'),


] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()








