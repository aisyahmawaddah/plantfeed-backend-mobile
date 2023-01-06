from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
    path('SearchMember', views.SearchMember, name='SearchMember'),
    path('SearchMember/<str:pk>', views.v2MainSearchbar, name='v2MainSearchbar'),
    path('sendMemberRequest/<str:userID>', views.sendMemberRequest, name='sendMemberRequest'),
    path('acceptMemberRequest/<str:requestID>', views.acceptMemberRequest, name='acceptMemberRequest'),
    path('ChatRoom/<str:room>', views.chatRoom, name='ChatRoom'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),


] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
