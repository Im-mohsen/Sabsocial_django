from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
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


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    message = forms.CharField(widget=forms.Textarea, required=True, label="پیام")
    name = forms.CharField(max_length=250, required=True, label="نام")
    email = forms.EmailField(max_length=250, required=True, label="ایمیل")
    phone = forms.CharField(min_length=11, max_length=11, required=True, label="شماره تماس")
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="موضوع")

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن عددی نیست!!")
            else:
                return phone


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description', 'tags']


class CommentForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) < 3:
                raise forms.ValidationError("نام کوتاه است!!")
            else:
                return name

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        # widgets = {
        #     'body': forms.TextInput(attrs={'class': 'body_boxe_form'}),
        #     'name': forms.TextInput(attrs={'class': 'boxes_form'}),
        #     'email': forms.TextInput(attrs={'class': 'boxes_form'})
        # }


class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)