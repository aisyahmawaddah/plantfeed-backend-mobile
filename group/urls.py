from django.contrib import admin
from django.urls import path
#from django.conf.urls import url, include
# from LOGIN import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .import api
# from group import api
from . import views
from .views import GroupTimelineCommentListView

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
    path('group-list/', api.GroupList.as_view(), name='group_list'),
    path('MainGroup/Filter_SoilTag',views.Group_SoilTag, name="Group_SoilTag"),
    path('MainGroup/Filter_PlantTag',views.Group_PlantTag, name="Group_PlantTag"),
    path('create-group/', api.createGroup),
    path('group-details/<int:pk>', GroupDetailView.as_view(), name="group-detail"),
    path('joined-group/<int:group_member_id>/', GroupMembershipAPIView.as_view()),
    path('create-group-membership/', api.create_group_membership, name='create_group_membership'),
    path('group-timelines/<int:group_fk_id>/', GroupTimelineListView.as_view(), name='group_timelines_list'),
    path('group-timelines/', GroupTimelineCreateView.as_view(), name='group-timelines'),
    path('group-timelines-comments/<int:feed_id>/', GroupTimelineCommentListView.as_view(), name='comment-list'),
    path('group-timelines-comments/create/', GroupTimelineCommentCreateView.as_view(), name='comment-create'),
    path('group-update/<int:pk>/update/', GroupUpdateAPIView.as_view(), name='group-update'),
    path('group/reply-comments/', api.replyComment, name ="reply-comment"),
    path('group/reply-comments/comment/<int:comment_id>/', ReplyCommentListByCommentID.as_view(),name= "view-reply"),
    path('group-memberships/<str:group_id>/', JoinedGroupMembershipAPIView.as_view(), name='group-memberships'),
    path('membership/delete/', MembershipDeleteAPIView.as_view(), name='membership-delete'),

    path('AddGroupSharing/<str:pk>',views.AddGroupSharing, name="AddGroupSharing"),
    path('Filter_SoilTag',views.Group_SoilTag, name="Group_SoilTag"),
    path('Filter_PlantTag',views.Group_PlantTag, name="Group_PlantTag"),
    path('GroupSharingComment/<str:pk>',views.addGSComment, name="GroupSharingComment"),
    path('PL-Sharing/<str:pk>', views.PLSharing, name="PL-Sharing"),
    path('PlantLink-Graph-API', views.PLGraphAPI, name="PlantLink-Graph-API"),
    path('proxy/', proxy_view, name='proxy'),
 

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()







