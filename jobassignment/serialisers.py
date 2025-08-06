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
    skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, required=False)
    # skills = serializers.ListField(child=serializers.CharField(),queryset=Skill.objects.all(), required=False)

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
        print("Skills data:", skills_data)

        # Create the Job
        job = Job.objects.create(**validated_data)
        print("Job created:", job)

        # Handle skills (Many-to-Many relationship)
        if skills_data:
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(name=skill_name.lower())  # Find or create skill by name
                job.skills.add(skill)   # Use the add method to link the skill to the job

        # Create Milestones
        for milestone_data in milestones_data:
            Milestone.objects.create(job=job, **milestone_data)

        print("Skills assigned to job:", job.skills.all())
        return job






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


class JobSerializer1(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)
    employer = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    
    # This field will be used for POST input
    skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    
    # This field will be used for GET output
    skill_names = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'employer', 'freelancer', 'is_archived', 'created_at', 'milestones', 'skills','skill_names']
        
    def get_skill_names(self, obj):
        # This is where the ManyRelatedManager is correctly iterated
        return [skill.id for skill in obj.skills.all()]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.method == 'POST':
            self.fields.pop('employer')
            self.fields.pop('freelancer')
            
    def create(self, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        skills_data = validated_data.pop('skills', [])
        user = self.context['request'].user
        
        job = Job.objects.create(employer=user, **validated_data)
        # job = Job.objects.create(employer=self.request.user, **validated_data)
        
        if skills_data:
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(name=skill_name.lower())
                job.skills.add(skill)
                
        for milestone_data in milestones_data:
            Milestone.objects.create(job=job, **milestone_data)
            
        return job
