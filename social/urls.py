from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = "social"

urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', views.user_login, name="login"),
    # path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('logout/', views.log_out, name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('user/edit', views.edit_user, name='edit_user'),

    path('ticket/', views.ticket, name="ticket"),
    path('reply/<int:ticket_id>', views.reply_to_ticket, name="reply_ticket"),
    path('tickets_list/', views.tickets_list, name='tickets_list'),
    path('ticket/<int:ticket_id>', views.ticket_detail, name='ticket_detail'),

    path('posts/', views.post_list, name="post_list"),
    path('posts/post/<slug:tag_slug>/', views.post_list, name="post_list_by_tag"),
    path('posts/create_post/', views.create_post, name="create_post"),
    path('posts/detail/<pk>', views.post_detail, name="post_detail"),
    path('posts/comments/<post_id>', views.add_comment, name="add_comment"),
    path('search/', views.post_search, name="post_search"),
    path('profile/create_post/<post_id>', views.edit_post, name="edit_post"),
    path('profile/delete_image/<image_id>', views.delete_image, name="delete_image"),
    path('profile/delete_post/<post_id>', views.delete_post, name="delete_post"),
    path('like_post/', views.like_post, name="like_post"),
    path('save_post/', views.save_post, name="save_post"),

    path('users/', views.user_list, name="user_list"),
    path('users/detail/<username>/', views.user_detail, name="user_detail"),
    path('users/follow/', views.user_follow, name="user_follow"),
    path('users_contact/<str:username>/<str:rel>/', views.user_contact, name="user_contact"),
    path('users_like/<post_id>', views.users_like, name="users_like"),

    # path('password_change/', auth_views.PasswordChangeView.as_view(success_url='done'),name='password_change'),
    path('password_change/', views.password_change, name='password_change'),
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_change/done/', views.password_change_done, name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(success_url='done'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(success_url='/password_reset/complete'),name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]