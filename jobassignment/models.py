from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_employer': True}, related_name='employer_jobs')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_freelancer': True}, related_name='freelancer_jobs')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
    

class Milestone(models.Model):
    job = models.ForeignKey(Job, related_name="milestones", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed_by_freelancer = models.BooleanField(default=False)
    is_approved_by_employer = models.BooleanField(default=False)
