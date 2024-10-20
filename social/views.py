from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import Post
from django.core.mail import send_mail
import datetime
from taggit.models import Tag
from django.db.models import Count


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


def post_list(request, tag_slug=None):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])  # many-to-many relations
    context = {
        "posts": posts,
        "tag": tag,
    }
    return render(request, "social/post_list.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("social:profile")
    else:
        form = PostForm()
    return render(request, "forms/create_post.html", {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_post = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:3]
    comments = post.comments.all()
    context = {
        "post": post,
        "similar_post": similar_post,
        "comments": comments,
    }
    return render(request, "social/post_detail.html", context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(request, "forms/comment.html", context)
