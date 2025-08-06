from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management.base import BaseCommand
import logging
from jobassignment.models import Job
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('old_job_apscheduler')

def archive_old_jobs():
    # Your archival logic (e.g., archive jobs with completed milestones)
   
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

    

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        print("===")
        scheduler.add_job(
            archive_old_jobs,
            # trigger=CronTrigger(hour=0, minute=0),  # runs daily at midnight
            trigger=CronTrigger(second=1),  # runs daily at midnight
            id="archive_old_jobs",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'archive_old_jobs'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
            print("===")

        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
