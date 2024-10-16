from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="account_image/", null=True, blank=True)
    job = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)