from django.urls import path , include
from .views import (JobViewSet, MilestoneViewSet  , TotalJobPerEmployerView,
                    TotalEarningPerFreelancerView,AverageMileStonePerJobView,JobWithPendingMilestoneView,
                    ApplyForJobView,JobUpdateAPIView,JobListApiView,ApproveJobApplicationView
                    ,export_large_user_csv,BulkCompletedMilestoneApi,AverageMilestoneValuePerJobApiView,JobCreateAPIView)
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
action = {
    'get':'list',
    'post':'create',
    'put':'update'
}
routers.register(r'', JobViewSet, basename='job')
# routers.register(r'', JobCreateAPIView, basename='job')
routers.register(r'milestone', MilestoneViewSet, basename='milestone')
urlpatterns = [
 
    # path('',JobViewSet,name="job"),
    path('job/', JobCreateAPIView.as_view(), name='create_job'),
    path('<int:pk>/', JobUpdateAPIView.as_view(), name='update_job'),
    path('list-job/', JobListApiView.as_view(), name='list_job'),


    # milestone
    path('milestone/',MilestoneViewSet.as_view(action),name="milestone-create"),
    path('<int:job_id>/list-milestone/',MilestoneViewSet.as_view(action),name="milestone-create"),
    path('milestone/<int:milestone_id>',MilestoneViewSet.as_view(action),name="milestone-update"),
    path('milestone/{milestone_id}/complete/',MilestoneViewSet.as_view(action),name="milestone-complete"),
    path('milestone/{milestone_id}/approve/',MilestoneViewSet.as_view(action),name="milestone-approve"),

    # dashboard api user
    path('total-job-per-employer/',TotalJobPerEmployerView.as_view(),name="total-job-per-employer"),
    path('total-freelancer-earning/',TotalEarningPerFreelancerView.as_view(),name="total-freelancer-earning"),
    path('average-milestone-value-per-job/',AverageMileStonePerJobView.as_view(),name="average-milestone-value-per-job"),
    path('job-with-pending-milestone/',JobWithPendingMilestoneView.as_view(),name="job-with-pending-milestone"),
    path('average-milestone-value-per-job-rowsql/',AverageMilestoneValuePerJobApiView.as_view(),name="job-with-pending-milestone"),

    path('<int:job_id>/apply/', ApplyForJobView.as_view(), name='apply-for-job'),
    path('{job_id}/approve-application/', JobViewSet.as_view(action), name='approve-job'),
    path('<int:pk>/approve/', ApproveJobApplicationView.as_view(), name='approve-job'),

    path('milestone/bulk-complete/',BulkCompletedMilestoneApi.as_view(),name = 'bulk-complete'),


    path('export-archive-csv/',export_large_user_csv,name='export_large_user_csv'),
    # path("",JobViewSet.as_view({'post':'create'}),name='jobs'),

    

]+routers.urls
