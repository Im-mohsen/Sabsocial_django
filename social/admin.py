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


# action function
def make_deactivation(modeladmin, request, queryset):
    result = queryset.update(active=False)
    if result==1:
        modeladmin.message_user(request, f"{result} Post were rejected")
    else:
        modeladmin.message_user(request, f"{result} Posts were rejected")


make_deactivation.short_description = 'رد پست'


def make_activation(modeladmin, request, queryset):
    result = queryset.update(active=True)
    if result==1:
        modeladmin.message_user(request, f"{result} Post were accepted")
    else:
        modeladmin.message_user(request, f"{result} Posts were accepted")


make_activation.short_description = 'تایید پست'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created', 'description', 'active']
    ordering = ["created"]
    search_fields = ["description"]
    actions = [make_deactivation,make_activation]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['post', 'title', 'created']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'created', 'email']
    list_filter = ["created", "updated"]
    search_fields = ["name", "body"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'is_opened']

@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'reply']


admin.site.register(Contact)
