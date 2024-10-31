from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from .models import Post,User
from django.core.mail import send_mail


@receiver(m2m_changed, sender=Post.likes.through)
def users_likes_changed(sender, instance, **kwargs):
    # کار هایی که میخواهیم بعد از دریافت سیگنال انجام شود را مینویسیم
    instance.total_likes = instance.likes.count()
    instance.save()


@receiver(post_delete, sender=Post)
def post_delete_admin(sender, instance, **kwargs):
    # کار هایی که میخواهیم بعد از دریافت سیگنال انجام شود را مینویسیم
    author = instance.author
    subject = f"Your post has been deleted"
    message = f"Your post has been deleted (ID: {instance.id})"
    send_mail(subject, message, 'mohsendarabi20003@gmail.com', [author.email], fail_silently=False)

@receiver(post_save, sender=User)
def user_auto_complete(sender, instance, created, **kwargs):
    # کار هایی که میخواهیم بعد از دریافت سیگنال انجام شود را مینویسیم
    if created:
        instance.first_name = 'نام شما'
        instance.last_name = 'نام خانوادگی شما'
        instance.email = 'enteryouremail@test.com'
        instance.bio = 'در مورد خود توضیحات بنویسید'
        instance.job = 'شغل را وارد کنید'
        instance.birth_date = '2001-01-01'

        instance.save()
