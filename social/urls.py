from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = "social"

urlpatterns = [
    path('', views.profile, name='profile'),
    # path('login', views.user_login, name="login"),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.register, name='register'),
    path('user/edit', views.edit_user, name='edit_user'),
    path('ticket/', views.ticket, name="ticket"),
    path('posts/', views.post_list, name="post_list"),
    path('posts/post/<slug:tag_slug>/', views.post_list, name="post_list_by_tag"),
    path('posts/create_post/', views.create_post, name="create_post"),
    path('posts/detail/<pk>', views.post_detail, name="post_detail"),
    path('posts/<post_id>/comment', views.post_comment, name="post_comment"),
    path('search/', views.post_search, name="post_search"),


    path('password_change/', auth_views.PasswordChangeView.as_view(success_url='done', template_name='registration/password_change_form.html'),name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(success_url='done'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(success_url='/password_reset/complete'),name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]