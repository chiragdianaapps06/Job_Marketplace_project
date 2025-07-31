from rest_framework import serializers
from .models import Job, Milestone

class MilestoneSerializer(serializers.ModelSerializer):
    
    
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'amount', 'is_completed_by_freelancer', 'is_approved_by_employer','job']

class JobSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'employer', 'freelancer', 'is_archived', 'created_at', 'milestones']

    def create(self, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        job = Job.objects.create(**validated_data)
        for milestone_data in milestones_data:
            Milestone.objects.create(job=job, **milestone_data)
        return job
