from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from .models import Post
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
