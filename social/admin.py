from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'email', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information',{'fields': ('date_of_birth', 'bio', 'photo', 'job', 'phone')}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author','created']
    ordering = ["created"]
    search_fields = ["description"]
