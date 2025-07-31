from django.urls import path , include
from .views import home , JobViewSet , MilestoneViewSet
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
action = {
    'get':'list',
    'post':'create'
}
routers.register(r'', JobViewSet, basename='job')
urlpatterns = [
 
    # path('',home,name="home"),
    # path('',JobViewSet.as_view(),name="job"),
    path('milestone/',MilestoneViewSet.as_view(action),name="milestone"),

]+routers.urls
