from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Job, Milestone
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@receiver(post_save,sender=Milestone)
def check_and_job_archive(sender,instance, **kwargs):

    job =instance.job

    if all(milestone.is_approved_by_employer  and milestone.is_completed_by_freelancer  for milestone in job.milestones.all()):

        job.is_archived = True
        job.save()
        print(f"Job {job.id} has been archived.")


from django.db.models.signals import pre_save

# Define the default employer (this could be an actual user or a generic "default" user)
DEFAULT_EMPLOYER_ID = 4  # Replace with the ID of the default employer user

@receiver(post_save, sender=CustomUser)
def reassign_jobs_on_soft_delete(sender, instance, **kwargs):
    # Check if the employer is being marked as deleted
    try:
        
        old_instance = CustomUser.objects.get(id=instance.id)  # Fetch the current instance from the DB
    except CustomUser.DoesNotExist:
        return  # If the user doesn't exist, we skip the reassign logic

    # If the `is_deleted` flag is being changed from False to True
    if old_instance.is_deleted == False and instance.is_deleted == True:
        if instance.is_employer:  # Check if the user is an employer
            # Reassign all jobs of this employer to the default employer\
            try:

                # default_employer = kwargs.get('default_employer', None)
            

                jobs = Job.objects.filter(employer=instance)
                default_employer = CustomUser.objects.get(id=DEFAULT_EMPLOYER_ID)
                # default_employer = CustomUser.objects.get(email = default_employer)

            
                jobs.update(employer=default_employer)
                print(f"All jobs of employer {instance.username} have been reassigned to the default employer.")
                
            
            except CustomUser.DoesNotExist:
                    # Handle case where the default employer doesn't exist
                    print(f"Default employer with email {default_employer} ")
