# from django.core.management.base import BaseCommand
# from jobassignment.models import Job

# class Command(BaseCommand):

#     def handle(self, *args, **kwargs):
#         job =Job.objects.all()

#         if all(milestone.is_approved_by_employer  and milestone.is_completed_by_freelancer  for milestone in job.milestones.all()):

#             job.is_archived = True
#             job.save()
#             print(f"Job {job.id} has been archived.")


from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from jobassignment.models import Job

class Command(BaseCommand):
    help = 'Archives old jobs where all milestones are completed and approved.'

    def handle(self, *args, **kwargs):
        # Get all jobs that are older than 30 days
        old_jobs = Job.objects.all()

        for job in old_jobs:
            if all(milestone.is_completed_by_freelancer and milestone.is_approved_by_employer for milestone in job.milestones.all()):
                job.is_archived = True
                job.save()
                # self.stdout.write(self.style.SUCCESS(f'Job {job.id} archived.'))
                print(f'Job {job.id} archived.')
            else:
                # self.stdout.write(self.style.NOTICE(f'Job {job.id} not archived due to incomplete or unapproved milestones.'))
                print(f'Job {job.id} not archived due to incomplete or unapproved milestones.')

        print("Archives old jobs where all milestones are completed and approved.")