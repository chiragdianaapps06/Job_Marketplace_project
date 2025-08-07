from django.urls import path , include
from .views import (LoginView, LoginView, SignUpView, OtpVerificationsView ,
                     LogoutView , ProtectedView, SoftDeleteUserAPIView,AddSkillToUserView, CustomUserListView,HardDeleteUserAPIView)
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView


routers = DefaultRouter()
routers.register(r'register',SignUpView,basename='register')
urlpatterns = [
    
    path('register/otp/',OtpVerificationsView.as_view(),name="otp-verification"),
    path('login/',LoginView.as_view(),name = "login"),

    path('generate-token/',TokenRefreshView.as_view(),name="refresh-access-token"),
    path('protected/',ProtectedView.as_view(),name="protected-view"),

    path('logout/',LogoutView.as_view(),name = "logout"),
    path('soft-delete/',SoftDeleteUserAPIView.as_view(),name = 'soft-delete'),
    path('delete/',HardDeleteUserAPIView.as_view(),name = 'hard-delete'),
    path('add-skills/',AddSkillToUserView.as_view(),name = 'add-skills'),
    path('list-user/',CustomUserListView.as_view(),name = 'list-user')
    
]+routers.urls
