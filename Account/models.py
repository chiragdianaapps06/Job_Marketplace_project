from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone


class TimestampModel(models.Model):
    createdAt=models.DateTimeField(auto_now_add=True)
    updatedAt=models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True



class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser,TimestampModel):
    email = models.EmailField(unique=True)
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, related_name='freelancers', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.username


class OtpVerification(TimestampModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    otp = models.IntegerField()
    
    

    def is_expired(self):
        return timezone.now() > self.updatedAt + timezone.timedelta(minutes=5)



