from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import Post
from django.core.mail import send_mail
import datetime
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity


# Create your views here.


def profile(request):
    if request.user.is_authenticated:
        user = request.user
        all_posts = Post.objects.filter(author=user)
        saved_posts = user.saved_posts.all()

        # صفحه بندی
        paginator = Paginator(all_posts, 5)
        page_number = request.GET.get('page', 1)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(page_number.num_pages)
        except PageNotAnInteger:
            page_obj = paginator.page(1)

        context = {
            'page_obj': page_obj,
            'saved_posts': saved_posts
        }
        return render(request, 'social/profile.html', context)
    else:
        return render(request, 'registration/login.html')


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("social:profile")
                else:
                    return HttpResponse("Your account is disabled.")
            else:
                return HttpResponse("Invalid login.")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {'form': form})


def log_out(request):
    logout(request)
    return render(request, 'registration/logged_out.html')


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
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])  # many-to-many relations

    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/list_ajax.html', {'posts': posts})
    context = {
        "posts": posts,
        "tag": tag,
    }
    return render(request, "social/post_list.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image_file=form.cleaned_data['image'], post=post)
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


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results1 = Post.objects.annotate(similarity=TrigramSimilarity('tags__name', query)). \
                filter(similarity__gt=0.1)
            results2 = Post.objects.annotate(similarity=TrigramSimilarity('description', query)). \
                filter(similarity__gt=0.1)
            results = (results1 | results2).order_by('-similarity').distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'social/search.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image_file=form.cleaned_data['image'], post=post)
            return redirect("social:profile")
    else:
        form = PostForm(instance=post)
    return render(request, "forms/create_post.html", {'form': form, 'post': post})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect('social:profile')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('social:profile')
    return render(request, 'forms/delete_post.html', {'post': post})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, 'پسورد شما با موفقیت تغییر کرد.')
            return redirect('done/')  # به صفحه‌ای که می‌خواهید بعد از تغییر به آن بروید
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'registration/password_change_form.html', {'form': form})


def password_change_done(request):
    return render(request, 'registration/password_change_done.html')


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post_likes_count = post.likes.count()
        response_data = {
            'likes_count': post_likes_count,
            'liked': liked,
        }
    else:
        response_data = {'error': 'Invalid post_id'}
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = Post.objects.get(id=post_id)
        # post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True

        return JsonResponse({'saved': saved})
    return JsonResponse({'errors': 'Invalid request'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})
