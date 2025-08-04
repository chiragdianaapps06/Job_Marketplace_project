from django.shortcuts import render
from rest_framework import viewsets
from .models import Job, Milestone , JobApplication, Skill
from .serialisers import JobSerializer, MilestoneSerializer 
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Count, Subquery, OuterRef, Sum , Avg, Q
from django.contrib.auth  import get_user_model
from rest_framework.response import Response
from rest_framework import status

CustomUser = get_user_model()


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_employer:
            return Job.objects.filter(employer=user)
        elif user.is_freelancer:
            return Job.objects.filter(freelancer__isnull=True)  # Jobs not yet assigned
        else:
            return Job.objects.none()


    def perform_create(self, serializer):
        # Ensure that the logged-in user is the employer
        
        if not self.request.user.is_employer:
              return Response({"message":"Only employers can create jobs."},status=status.HTTP_401_UNAUTHORIZED)
        # Assign the employer automatically to the job
        serializer.save(employer=self.request.user)
        # return Response({"message":"job save successfully.","data":serializer.data},status=status.HTTP_200_OK)

     

    def perform_update(self, serializer):
        job = self.get_object()
        if self.request.user != job.employer:
            raise PermissionDenied("You are not allowed to update this job.")
        serializer.save(employer = self.request.user)

# class JobViewSet(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Ensure that the logged-in user is the employer
#         if not request.user.is_employer:
#             return Response({"message":"Only employers can create jobs."},status=status.HTTP_401_UNAUTHORIZED)

#         # Add the employer to the request data automatically
#         data = request.data.copy()
#         data['employer'] = request.user.id  # Automatically assign the logged-in user as employer

#         # Serialize the data
#         serializer = JobSerializer(data=data)

#         # Validate and save the job
#         if serializer.is_valid():
#             job = serializer.save()  # Save the job object

#             # Return the serialized job data as the response
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         # If the serializer is invalid, return errors
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        milestone = self.get_object()
        print("===",request.user)        
        print("===",milestone.job.freelancer)        

        
        # Check if the user is the freelancer assigned to the job
        if milestone.job.freelancer == request.user:
            milestone.is_completed_by_freelancer = True
            milestone.save()
            return Response({"status": "Milestone completed!"}, status=status.HTTP_200_OK)
        return Response({"error": "You are not assigned to this job!"}, status=status.HTTP_400_BAD_REQUEST)
    

    # Employer approves the milestone after completion by freelancer
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        milestone = self.get_object()
        print("===",request.user)        
        print("===",milestone.job.employer)        
        print("===",milestone.job.freelancer)        

        # Check if the user is the employer of the job
        if milestone.job.employer == request.user:
            if milestone.is_completed_by_freelancer:
                milestone.is_approved_by_employer = True
                milestone.save()
                return Response({"status": "Milestone approved!"}, status=status.HTTP_200_OK)
            
            return Response({"error": "Milestone must be completed by freelancer first!"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Yout are not authorized to this job"}, status=status.HTTP_400_BAD_REQUEST)

from .serialisers import EmployerJobCountSerializer

class TotalJobPerEmployerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        try:        
            # Calculate the total number of jobs per employer
            employers = CustomUser.objects.filter(is_employer=True).annotate(total_jobs=Count('employer_jobs'))

            if not employers.exists():
                return Response({
                    "message": "No Employer data exist.",
                    "data": []
                }, status=status.HTTP_204_NO_CONTENT)  

            for employer in employers:
                print(employer.username, employer.total_jobs)

            serializer = EmployerJobCountSerializer(employers, many=True)

            return Response({"message":"ftech total job per emplyer successfully.","data": serializer.data},status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"message":"Internal server error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TotalEarningPerFreelancerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        try:

            #finding Total Earning per freelancer 
            freelancers = CustomUser.objects.filter(is_freelancer=True).annotate(
                total_earnings = Subquery(
                    Milestone.objects.filter(
                      job__freelancer=OuterRef('pk'),
                      is_completed_by_freelancer = False

                    ).values('job__freelancer').annotate(total=Sum('amount')).values('total')[:1]
                ))
            
            if not freelancers.exists():
                return Response({
                    "message": "No freelancer data available.",
                    "data": []
                }, status=status.HTTP_204_NO_CONTENT)  
            

            serializer = EmployerJobCountSerializer(freelancers,many=True)
        
            return Response({"message":"Fetch total earning of freelancer successfully.","data":serializer.data},status=status.HTTP_200_OK)
            
            

        except Exception as e:
             return Response({"message":"Internal server error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class AverageMileStonePerJobView(APIView):

    def get(self,request,*args, **kwargs):
        try:

            #finding Averaage milestone per job

            jobs = Job.objects.annotate(
                avg_milestone_value = Subquery(
                    Milestone.objects.filter(
                         job=OuterRef('pk')
                    ).values('job').annotate(average=Avg('amount')).values('average')[:1]
                )
            )

            if not jobs.exists():
                return Response({
                    "message": "No Milestone data available.",
                    "data": []
                }, status=status.HTTP_204_NO_CONTENT)  
            
            
            data =[
                    {'id':job.id,'title': job.title, 'avg_milestone_value': job.avg_milestone_value}
                    for job in jobs
                ]
      
            
            
        
       
            return Response({"message":"Fetch total earning of freelancer successfully.","average_milestone_value":data},status=status.HTTP_200_OK)
            
            

        except Exception as e:
             return Response({"message":"Internal server error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class JobWithPendingMilestoneView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        try:

            # finding Job with pending milestone
            jobs_with_pending_milestones = Job.objects.annotate(
                pending_milestones=Count(
                    'milestones',
                    filter=Q(milestones__is_completed_by_freelancer=False, milestones__is_approved_by_employer=False)
                )
            ).filter(pending_milestones__gt=0)

            if not jobs_with_pending_milestones.exists():
                return Response({
                    "message": "No pending milestone data available.",
                    "data": []
                }, status=status.HTTP_204_NO_CONTENT)  
            
            data =  [
                    {'id':job.id,'title': job.title, 'pending_milestones': job.pending_milestones}
                    for job in jobs_with_pending_milestones
                ]
      
            
       
            return Response({"message":"Fetch job with pending milestone.","job_with_pending_mile":data},status=status.HTTP_200_OK)
            
            

        except Exception as e:
             return Response({"message":"Internal server error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplyForJobView(APIView):

    permission_classes =  [IsAuthenticated]

    def post(self,request,job_id):
        user = request.user
        if not  user.is_freelancer :
            return Response({"message":"Only freelancer are allow to apply for the job."},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            job = Job.objects.get(id = job_id)

        except Job.DoesNotExist:
            return Response({"message":"Job you want to access is not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if JobApplication.objects.filter(job = job, freelancer = user).exists():
            return Response({"message":"you have already applied ."},status=status.HTTP_400_BAD_REQUEST)
        
        JobApplication.objects.create(job =job,freelancer = user, cover_letter = request.data.get('cover_letter'))

        return Response({"message":"Your Job application sumbit Successfully."},status=status.HTTP_200_OK)
    