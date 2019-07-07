from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
# class User(models.Model):
#     username = models.CharField(max_length=20),
#     password = models.CharField(max_length=20),
#     mobile = models.CharField(max_length=11)
class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True)