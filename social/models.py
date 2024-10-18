from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
# Create your models here.


class User(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="account_image/", null=True, blank=True)
    job = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    description = models.TextField(verbose_name="توضیحات")
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    tags = TaggableManager()
    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.author.first_name
