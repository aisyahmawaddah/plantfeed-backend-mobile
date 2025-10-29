from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
#from django.conf.urls import url
#from member.views import LoginView
from .import api
#from member.api import PersonCreateView, UserAuthentication, UserList
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.UserReg, name='Register'),
    path('Login', views.login, name='Login'),
    path('Home', views.homepage, name='Home'),
    path('HomeAdmin', views.homepageAdmin, name='HomeAdmin'),
    path('Logout', views.logout, name='Logout'),
    path('EditProfile', views.EditProfile, name='EditProfile'),
    path('ViewProfile', views.Profile, name='ViewProfile'),
    path('MemberMainPage', views.MainMember, name='MemberMainPage'),
    path('OpenProfileMember/<str:pk>', views.openProfileMember, name='OpenProfileMember'),   
    path('SearchMember', views.SearchMember, name='SearchMember'),
    path('SearchMember/<str:pk>', views.v2MainSearchbar, name='v2MainSearchbar'),
    path('DeleteMemberRequest/<str:pk>', views.deleteMemberReq, name='DeleteMemberRequest'),
    path('DeleteMember/<str:pk1>/<str:pk2>', views.deleteMember, name='DeleteMember'),
    path('sendMemberRequest/<str:userID>', views.sendMemberRequest, name='sendMemberRequest'),
    path('acceptMemberRequest/<str:requestID>', views.acceptMemberRequest, name='acceptMemberRequest'),
    path('ChatRoom/<str:room>', views.chatRoom, name='ChatRoom'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
    path("check_username_availability", views.check_username_availability, name="check_username_availability"),
    path("check_email_availability", views.check_email_availability, name="check_email_availability"),
    #url(r'^api/users_lists/$', UserList.as_view(), name='user_list'),
    #url(r'^api/users_list/(?P<id>\d+)/$', UserDetail.as_view(), name='user_list'),
    #url(r'^api/auth/$', UserAuthentication.as_view(), name='User Authentication API'),
    #url(r'^rest-auth/', include('rest_auth.urls')),
    #url(r'^rest-auth/registration/', include('rest_auth.registration.urls'))
    #path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    #path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('userlist/', views.user_list, name='userlist'),
    #path('login', obtain_auth_token, name='login')
    path('users/login/', api.login_user, name='login'),
    #path('users/update/', api.UpdateProfileView, name='update'),
    path('users/token/<pk>', api.getUserFromToken, name='user-token'),
    path('users/updateProfile/<int:pk>/', api.UpdateProfileView.as_view(), name='auth_update_profile'),
    #path('users/post-feed/', api.postFeed),
    #path('users/feed/<int:creator_id>/', api.CreatorFeedView.as_view(), name='creator_feed'),
    #path('users/feed/delete/', api.DeleteFeedView.as_view(), name='delete_feed'),
    #path('users/feed/<int:creator_id>/', api.CreatorFeedView.as_view(), name='creator_feed'),

] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
