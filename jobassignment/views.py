from rest_framework import viewsets
from .models import Job, Milestone , JobApplication, Skill
from .serialisers import JobSerializer, MilestoneSerializer ,JobSerializer1
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Count, Subquery, OuterRef, Sum , Avg, Q
from django.contrib.auth  import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from .serialisers import EmployerJobCountSerializer
from django.db import transaction
CustomUser = get_user_model()

# import libraries for csv export task
from rest_framework.decorators import permission_classes, api_view
from django.http import StreamingHttpResponse
import csv

# import logger
from .logger import get_logger
logger = get_logger("job-task-logger")

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer1
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
            return Response({"message": "Only employers can create jobs."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create the job with the employer set to the current user
        job = serializer.save()

        # Process and add skills (many-to-many relationship)
        skills_data = self.request.data.get('skills', [])
        if skills_data:
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(name=skill_name.lower())  # Ensure uniqueness by converting to lowercase
                job.skills.add(skill)

        return Response({
            "message": "Job saved successfully.",
            "data": JobSerializer1(job).data
        }, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     # Ensure that the logged-in user is the employer
        
    #     if not self.request.user.is_employer:
    #           return Response({"message":"Only employers can create jobs."},status=status.HTTP_401_UNAUTHORIZED)
    #     # Assign the employer automatically to the job
        # job = serializer.save(employer=self.request.user)

        # skills_data = self.request.data.get('skills', [])
        # if skills_data:
        #     for skill_name in skills_data:
        #         skill, created = Skill.objects.get_or_create(name=skill_name.lower())  # Ensure uniqueness by converting to lowercase
        #         job.skills.add(skill)

        # return Response({"message":"job save successfully.","data":JobSerializer(job).data},status=status.HTTP_200_OK)

     

    def perform_update(self, serializer):
        job = self.get_object()
        if self.request.user != job.employer:
            raise PermissionDenied("You are not allowed to update this job.")
        serializer.save(employer = self.request.user)



    @action(detail=True, methods=['post'], url_path='approve-application')
    def approve_application(self, request, pk=None):
        job = self.get_object()
        print("===",job)
        freelancer_id = request.data.get('freelancer_id')
        print("===",freelancer_id)
        if not freelancer_id:

            return Response({"error":"freelancer is not passed."},status=status.HTTP_400_BAD_REQUEST)

        try:
            application = JobApplication.objects.get(job=job, freelancer__id=freelancer_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        # Skill Matching Logic
        job_skills = set(job.skills.values_list('id', flat=True))
        freelancer_skills = set(application.freelancer.skills.values_list('id', flat=True))

        if not job_skills.issubset(freelancer_skills):
            return Response({"error": "Freelancer's skills do not match job requirements."}, status=status.HTTP_400_BAD_REQUEST)

        # Approve Application and Assign Freelancer
        application.is_approved = True
        application.save()
        job.freelancer = application.freelancer
        job.save()

        return Response({"status": f"Freelancer {application.freelancer.username} assigned to job."}, status=status.HTTP_200_OK)  




class JobCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):
        skills_data = request.data.get('skills', [])  # Get skills from request body
        milestones_data = request.data.get('milestones', [])  # Get milestones from request body
        title = request.data.get('title', None)
        description = request.data.get('description', None)

        if not title or not description:
            raise PermissionDenied("Only employers can create jobs.")

        job_data = {
            'title': title,
            'description': description,
        }

        # Check if user is an employer
        if not request.user.is_employer:
            return Response({"message": "Only employers can create jobs."}, status=status.HTTP_403_FORBIDDEN)

        # Create the Job
        job = Job.objects.create(**job_data, employer=request.user)

        # Handle Skills - Associate skills with the job
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name.lower())
            skills.append(skill)
        skill
        
        job.skills.set(skills)  # Set the Many-to-Many relationship for skills
        job.save()

        # Handle Milestones - Create related milestones
        for milestone_data in milestones_data:
            Milestone.objects.create(job=job, **milestone_data)

        return Response({"message": "Job created successfully.", "job": JobSerializer(job).data}, status=status.HTTP_201_CREATED)


class JobUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"message": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        if job.employer != request.user:
            return Response({"message": "You do not have permission to update this job."}, status=status.HTTP_403_FORBIDDEN)

        skills_data = request.data.get('skills', [])
        milestones_data = request.data.get('milestones', [])
        title = request.data.get('title', job.title)
        description = request.data.get('description', job.description)

        job.title = title
        job.description = description
        job.save()

        # Handle Skills - Update Many-to-Many relationship
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name.lower())
            skills.append(skill)

        job.skills.set(skills)  # Update the skills
        job.save()

        # Handle Milestones - Update or create
        for milestone_data in milestones_data:
            milestone_id = milestone_data.get('id', None)
            if milestone_id:
                try:
                    milestone = Milestone.objects.get(id=milestone_id, job=job)
                    for attr, value in milestone_data.items():
                        setattr(milestone, attr, value)
                    milestone.save()
                except Milestone.DoesNotExist:
                    Milestone.objects.create(job=job, **milestone_data)
            else:
                Milestone.objects.create(job=job, **milestone_data)

        return Response({"message": "Job updated successfully.", "job": JobSerializer(job).data}, status=status.HTTP_200_OK)


class JobListApiView(APIView):
    """
    API View to list all jobs for the logged-in user (employer or freelancer).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of jobs based on the user's role.
        - Employers see their own jobs.
        - Freelancers see jobs that are not yet assigned to anyone.
        """
        user = request.user
        
        # Filter jobs based on the user role
        if user.is_employer:
            jobs = Job.objects.filter(employer=user)
        elif user.is_freelancer:
            jobs = Job.objects.filter(freelancer__isnull=True)  # Only jobs not assigned to a freelancer
        else:
            jobs = Job.objects.none()

        # Serialize the data
        serializer = JobSerializer(jobs, many=True)

        # Return serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)





class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        milestone = self.get_object()
        print("===",request.user)        
        print("===",milestone.job.freelancer)   

        if not request.user.is_freelancer:
            return Response({"message":"you are not freelancer"},status=status.HTTP_401_UNAUTHORIZED)

        
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
    


class ApproveJobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        # Get the job using the primary key passed in the URL
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_employer :
            raise PermissionDenied("Only the employer can approve the applications.")
        # Ensure the user is the employer of this job
        if job.employer != request.user:
            raise PermissionDenied("Only job employer can approve applications.")

        # Get freelancer_id from the request body
        freelancer_id = request.data.get('freelancer_id')

        if not freelancer_id:
            return Response({"error": "Freelancer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the application for this job and freelancer
        try:
            application = JobApplication.objects.get(job=job, freelancer__id=freelancer_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        # Skill Matching Logic
        job_skills = set(job.skills.values_list('id', flat=True))  # skills required by job
        freelancer_skills = set(application.freelancer.skills.values_list('id', flat=True))  # skills of freelancer

        if not job_skills.issubset(freelancer_skills):
            return Response({"error": "Freelancer's skills do not match job requirements."}, status=status.HTTP_400_BAD_REQUEST)

        # Atomic transaction for updating application and job
        try:
            with transaction.atomic():
                # Approve the application and assign freelancer to job
                application.is_approved = True
                application.save()
                job.freelancer = application.freelancer
                job.save()
            
            return Response({"status": f"Freelancer {application.freelancer.username} assigned to job."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value
    
@api_view(http_method_names=['GET'])
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def export_large_user_csv(request):
    """
    Exports a large dataset of Orders as CSV using streaming response.
    Admin-only access. Handles exceptions with proper logging and JSON error.
    """
    try:
        rows = Job.objects.filter(is_archived = True).values_list('title','description','employer','freelancer','skills').iterator()
        # rows = Order.objects.all()

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        # Generator expression for streaming
        
        def row_generator():
            i=0
            yield ['title','description','employer','freelancer','skills']  # headers
            for row in rows:
                print("=====",i)
                i+=1
                yield row
            logger.info("Finished generating CSV rows.")

        response = StreamingHttpResponse(
            (writer.writerow(row) for row in row_generator()),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename="order_data_large.csv"'

        logger.info("CSV export completed successfully.")

        return response

    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}", exc_info=True)
        return Response(
            {"error": "An error occurred while exporting the CSV."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

class BulkCompletedMilestoneApi(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            print("Request Data: %s", request.data)
            milestone_ids = request.data.get("milestone_ids",[])

            print("----",milestone_ids)

            # check milestone list is emplty or not
            if not milestone_ids:
                return Response({"error": "No milestone IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
            
            # fetch milestone assign to loggin user which are not completed
            milestones = Milestone.objects.filter(id__in=milestone_ids,job__freelancer = request.user,is_completed_by_freelancer = False)


            if not milestones:
                return Response({"message":"No valid Milestone found for completion"},status=status.HTTP_404_NOT_FOUND)
            for milestone in milestones:
                milestone.is_completed_by_freelancer = True

            with transaction.atomic():
                Milestone.objects.bulk_update(milestones,['is_completed_by_freelancer'])

            return Response({"message":""},status=status.HTTP_200_OK)

        except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )