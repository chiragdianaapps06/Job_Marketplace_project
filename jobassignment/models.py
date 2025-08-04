from django.db import models
from django.contrib.auth import get_user_model
from Account.models import Skill

CustomUser = get_user_model()
# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_employer': True}, related_name='employer_jobs')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_freelancer': True}, related_name='freelancer_jobs')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(Skill, related_name='jobs', blank=True)


    def __str__(self):
        return self.title
    
    def get_skills(self, obj):
        # Ensure you call `.all()` to access related skill objects
        return [skill.name for skill in obj.skills.all()]

    

class Milestone(models.Model):
    job = models.ForeignKey(Job, related_name="milestones", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed_by_freelancer = models.BooleanField(default=False)
    is_approved_by_employer = models.BooleanField(default=False)


class JobApplication(models.Model):
    job =  models.ForeignKey(Job,on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(CustomUser,on_delete=models.CASCADE, limit_choices_to={'is_freelancer': True})
    cover_letter = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job','freelancer')
    def __str__(self):
        return f"{self.freelancer.username} is applied for {self.job.id - self.job.title}"