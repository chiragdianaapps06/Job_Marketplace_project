from rest_framework import serializers
from .models import Job, Milestone

from django.contrib.auth import get_user_model


CustomUser = get_user_model()

class MilestoneSerializer(serializers.ModelSerializer):
    
    
    # job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'amount', 'is_completed_by_freelancer', 'is_approved_by_employer']

class JobSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)
    employer = serializers.PrimaryKeyRelatedField( required=False, read_only=True)    


    class Meta:
        model = Job
        fields = ['id', 'title', 'description','employer', 'freelancer', 'is_archived', 'created_at', 'milestones']

    
    def __init__(self, *args, **kwargs):
        # Initialize the parent class
        super().__init__(*args, **kwargs)

    
        
        # Check if the request method is GET or POST
        request = self.context.get('request', None)
        
        if request and request.method == 'POST':
            # If it's a POST request, remove the employer field (not required when creating a job)
            self.fields.pop('employer')

    
    
    def create(self, validated_data):
            

            milestones_data = validated_data.pop('milestones', [])
            job = Job.objects.create(**validated_data)

            # Create the milestones associated with this job
            for milestone_data in milestones_data:
                Milestone.objects.create(job=job, **milestone_data)

            return job


# class JobSerializer(serializers.ModelSerializer):
#     milestones = MilestoneSerializer(many=True)  # Nested serializer for milestones

#     class Meta:
#         model = Job
#         fields = ['id', 'title', 'description', 'employer', 'freelancer', 'is_archived', 'created_at', 'milestones']

#     def create(self, validated_data):
#         """
#         Custom create method to handle milestones when creating a job.
#         """
#         # Extract milestones data
#         milestones_data = validated_data.pop('milestones', [])

#         # Create the Job object
#         job = Job.objects.create(**validated_data)

#         # Create Milestone objects and associate them with the Job
#         for milestone_data in milestones_data:
#             Milestone.objects.create(job=job, **milestone_data)

#         return job

#     def update(self, instance, validated_data):
#         """
#         Custom update method if necessary. Here it's just a placeholder.
#         """
#         milestones_data = validated_data.pop('milestones', [])
#         instance = super().update(instance, validated_data)

#         # Update Milestones associated with this Job
#         for milestone_data in milestones_data:
#             Milestone.objects.update_or_create(job=instance, **milestone_data)

#         return instance

class EmployerJobCountSerializer(serializers.ModelSerializer):
    total_jobs = serializers.IntegerField(required=False)
    total_earnings = serializers.IntegerField(read_only=True,required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'total_jobs','total_earnings']



# class FreelancerTotalEarningSerializer(serializers.ModelSerializer):

#     total_earnings = serializers.IntegerField()
#     class Meta:
#         model= CustomUser
#         fields = ['username','total_earnings']

    