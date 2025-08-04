from django.urls import path , include
from .views import (JobViewSet , MilestoneViewSet  , TotalJobPerEmployerView,
                    TotalEarningPerFreelancerView,AverageMileStonePerJobView,JobWithPendingMilestoneView,
                    ApplyForJobView)
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
action = {
    'get':'list',
    'post':'create',
    'put':'update'
}
routers.register(r'', JobViewSet, basename='job')
routers.register(r'milestone', MilestoneViewSet, basename='milestone')
urlpatterns = [
 
    # path('',JobViewSet,name="job"),
  
    path('milestone/',MilestoneViewSet.as_view(action),name="milestone"),
    # path('milestone/{milestone_id}/complete/',MilestoneViewSet.as_view(action),name="milestone-complete"),
    # path('milestone/{milestone_id}/approve/',MilestoneViewSet.as_view(action),name="milestone-approve"),
    path('total-job-per-employer/',TotalJobPerEmployerView.as_view(),name="total-job-per-employer"),
    path('total-freelancer-earning/',TotalEarningPerFreelancerView.as_view(),name="total-freelancer-earning"),
    path('average-milestone-value-per-job/',AverageMileStonePerJobView.as_view(),name="average-milestone-value-per-job"),
    path('job-with-pending-milestone/',JobWithPendingMilestoneView.as_view(),name="job-with-pending-milestone"),

    path('<int:job_id>/apply/', ApplyForJobView.as_view(), name='apply-for-job'),

    

]+routers.urls
