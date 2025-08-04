from rest_framework import serializers
from .models import Job, Milestone , JobApplication

from django.contrib.auth import get_user_model
from Account.models import Skill
from rest_framework import serializers
from .models import Job, Milestone, Skill

CustomUser = get_user_model()

class MilestoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    
    # job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'amount', 'is_completed_by_freelancer', 'is_approved_by_employer']








class JobSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)
    employer = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    # skills = serializers.PrimaryKeyRelatedField(required = False,read_only = True)

    # skills = serializers.StringRelatedField(many=True)    

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'employer', 'freelancer', 'is_archived', 'created_at', 'milestones', 'skills']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.method == 'POST':
            self.fields.pop('employer')  # Remove employer field in POST
            self.fields.pop('freelancer')  # Remove freelancer field in POST

    def create(self, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        skills_data = validated_data.pop('skills', [])
        print("job----",skills_data)

        # Create the Job
        job = Job.objects.create(**validated_data)
        print("Job created: ", job)

      
        # skills = []
        # for skill_name in skills_data:
        #     skill, created = Skill.objects.get_or_create(name=skill_name.lower())  # Ensure skill exists
        #     skills.append(skill)

        
        # job.skills.set(skills)  # Set the skills on the Job instance
        # job.save()
        
        # print("Skills assigned to job:", job.skills.all()) 

        if skills_data:
            skills = []
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(name=skill_name.lower())
                skills.append(skill)

            # Associate the skills with the job (Many-to-Many relationship)
            job.skills.set(skills)
        
        # Create Milestones
        for milestone_data in milestones_data:
            print("-----")
            Milestone.objects.create(job=job, **milestone_data)
        print(job)
        return job

    def update(self, instance, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        skills_data = validated_data.pop('skills', [])

        # Update Job fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create milestones
        for milestone_data in milestones_data:
            milestone_id = milestone_data.get('id', None)
            if milestone_id:
                try:
                    milestone = Milestone.objects.get(id=milestone_id, job=instance)
                    for attr, value in milestone_data.items():
                        setattr(milestone, attr, value)
                    milestone.save()
                except Exception:
                    Milestone.objects.create(job=instance, **milestone_data)
            else:
                Milestone.objects.create(job=instance, **milestone_data)

        # Handle Skills
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name.lower())  # Ensure skill exists
            skills.append(skill)

        # Associate skills with the job
        instance.skills.set(skills)

        return instance



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
        fields = ['id','username', 'total_jobs','total_earnings']



# class FreelancerTotalEarningSerializer(serializers.ModelSerializer):

#     total_earnings = serializers.IntegerField()
#     class Meta:
#         model= CustomUser
#         fields = ['username','total_earnings']



class JobApplicationsSerilizer(serializers.ModelSerializer):

    class Meta:
        model =  JobApplication
        fields = ['id','job','freelancer','cover_letter','is_approved']


