from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from .models import Post, Contact
from django.core.mail import send_mail
import datetime
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib import messages

# Create your views here.


def profile(request):
    if request.user.is_authenticated:
        # user = request.user
        user = User.objects.prefetch_related('followers', 'following').get(id=request.user.id)
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


@login_required
def ticket(request):
    user = request.user
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_obj = form.save(commit=False)
            ticket_obj.user = user
            ticket_obj.save()

            cd = form.cleaned_data
            now = datetime.datetime.now()
            message = (f"Sender: {user}\ncontent: {cd['content']}\nemail: {user.email}\ndate: {now.strftime("%Y-%m-%d %H:%M")}"
                       f"\n\nreply to ticket: {request.build_absolute_uri(f'/reply/{ticket_obj.id}')}")
            send_mail(cd['subject'], message, 'mohsendarabi20003@gmail.com', ['pcnoo2023@gmail.com'], fail_silently=False)
            messages.success(request, 'ایمیل شما با موفقیت ارسال شد.')
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


@staff_member_required
def reply_to_ticket(request, ticket_id):
    sent_ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == "POST":
        form = ReplyTicketForm(request.POST)
        if form.is_valid():
            if sent_ticket.is_opened == True:
                reply_obj = form.save(commit=False)
                reply_obj.ticket = sent_ticket
                reply_obj.save()

                subject = 'پاسخ به تیکت شما'
                message = (f"سلام ادمین به تیکت شما پاسخ داد. هم اکنون میتوانید از لینک زیر آن را مشاهده کنید.\n{request.build_absolute_uri(f'/ticket/{ticket_id}')}")
                send_mail(subject, message, 'mohsendarabi20003@gmail.com', [sent_ticket.user.email],
                          fail_silently=False)

                messages.success(request, 'پاسخ شما با موفقیت ارسال شد.')
                sent_ticket.is_opened = False
                sent_ticket.save()
            else:
                messages.success(request, 'این صفحه چت بسته شده')
    else:
        form = ReplyTicketForm()
    return render(request, "forms/replies.html", {"form": form, "ticket": sent_ticket})


def tickets_list(request):
    user = request.user

    if user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(user=user)

    return render(request,'social/ticket_list.html', {'tickets': tickets})


def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    return render(request,'social/ticket_detail.html', {'ticket': ticket})


def post_list(request, tag_slug=None):
    posts = Post.objects.select_related('author').order_by('-total_likes')
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

    comment_form = CommentForm()
    comments = post.post_comments.all()

    context = {
        "post": post,
        "similar_post": similar_post,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "social/post_detail.html", context)


@require_POST
def add_comment(request, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, pk=post_id)

            comment = form.save(commit=False)
            comment.post = Post.objects.get(id=post_id)
            comment.user = request.user
            comment.save()

            response = {
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'comment_count': post.post_comments.count(),
            }
            return JsonResponse(response)
    else:
        return JsonResponse({'status': 'error', 'errors': 'Invalid data!'})

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
    following = user.get_following()
    followers = user.get_followers()
    context = {
        'user': user,
        'following': following,
        'followers': followers,
    }
    return render(request, 'user/user_detail.html', context)


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            response_data = {
                'follow': follow,
                'followers_count': followers_count,
                'following_count': following_count,
            }
            return JsonResponse(response_data)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid post_id'})
    return JsonResponse({'error': 'Invalid request'})


def user_contact(request, username, rel):
    user = get_object_or_404(User, username=username, is_active=True)
    if rel == 'followers':
        contacts = user.get_following()
    elif rel == 'following':
        contacts = user.get_following()
    else:
        contacts = None
    return render(request, 'user/user_contact.html', {'users': contacts, 'rel': rel})


def users_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    return render(request, 'user/users_like.html', {'post': post, 'post_id': post_id})
