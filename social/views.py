from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse
from .forms import *
from .models import Post
from django.core.mail import send_mail
import datetime
# Create your views here.


def profile(request):
    return HttpResponse("Hello, world. You're at the blog index.")


def log_out(request):
    logout(request)
    # return redirect(request.META.get('HTTP_REFERER'))
    return HttpResponse("You've been logged out.")


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {'form': form})


@login_required
def edit_user(request):
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user, files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            return redirect('social:profile')
    else:
        user_form = UserEditForm(instance=request.user)
    context = {
        "user_form": user_form
    }
    return render(request, 'registration/edit_user.html', context)


def ticket(request):
    sent = False
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            now = datetime.datetime.now()
            message = f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n{now.strftime("%Y-%m-%d %H:%M")}\n\n{cd['message']}"
            send_mail(cd['subject'], message, cd['email'], ['pcnoo2023@gmail.com'], fail_silently=False)
            # ticket_obj = Ticket.objects.create(message=cd['message'], name=cd['name'], email=cd['email']
            #                                    , phone=cd['phone'], subject=cd['subject'])
            sent = True
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form, 'sent': sent})


def post_list(request):
    posts = Post.objects.all()
    context = {
        "posts": posts,
    }
    return render(request, "social/post_list.html", context)