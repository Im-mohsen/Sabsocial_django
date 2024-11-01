from django import forms
from .models import *
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import AuthenticationForm


# class LoginForm(AuthenticationForm):
#     username = forms.CharField(max_length=250, required=True)
#     password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label="رمز عبور")
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput, label="تکرار رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("رمز عبورها باهم یکسان نیستند!")
        return cd['password2']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("phone already exists!")
        return phone


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email', 'date_of_birth', 'bio', 'photo', 'job']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise forms.ValidationError("phone already exists!")
        return phone

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError("username already exists!")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError("email already exists!")
        return email


# class TicketForm(forms.Form):
#     SUBJECT_CHOICES = (
#         ('پیشنهاد', 'پیشنهاد'),
#         ('انتقاد', 'انتقاد'),
#         ('گزارش', 'گزارش'),
#     )
#     message = forms.CharField(widget=forms.Textarea, required=True, label="پیام")
#     name = forms.CharField(max_length=250, required=True, label="نام")
#     email = forms.EmailField(max_length=250, required=True, label="ایمیل")
#     phone = forms.CharField(min_length=11, max_length=11, required=True, label="شماره تماس")
#     subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="موضوع")
# 
#     def clean_phone(self):
#         phone = self.cleaned_data['phone']
#         if phone:
#             if not phone.isnumeric():
#                 raise forms.ValidationError("شماره تلفن عددی نیست!!")
#             else:
#                 return phone
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'content']


class ReplyTicketForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ['reply']


class PostForm(forms.ModelForm):
    image = forms.ImageField(label="تصویر")

    class Meta:
        model = Post
        fields = ['description', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']



class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)


class CustomPasswordChangeForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)