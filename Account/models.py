from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone


class TimestampModel(models.Model):
    createdAt=models.DateTimeField(auto_now_add=True)
    updatedAt=models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class CustomUser(AbstractUser,TimestampModel):
    email = models.EmailField(unique=True)
    is_employer = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)

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







