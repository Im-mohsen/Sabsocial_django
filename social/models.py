from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from django.urls import reverse
from django_resized import ResizedImageField
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
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
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

    def get_absolute_url(self):
        return reverse("social:post_detail", args=[self.id])


def user_directory_path(instance, filename):
    user = instance.post.author.username
    return f"post_images/{user}/{filename}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    image_file = ResizedImageField(upload_to=user_directory_path, size=[600, 340], quality=80,
                                   crop=['middle', 'center'], null=True, blank=True)
    title = models.CharField(max_length=250, verbose_name="عنوان عکس", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویر ها"

    def __str__(self):
        return f"title: {self.title}" if self.title else f"image_name: {self.image_file}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, verbose_name="نام")
    body = models.TextField(verbose_name="متن کامنت")
    email = models.EmailField(max_length=250, verbose_name="ایمیل")
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return f"{self.name}: {self.post}"
