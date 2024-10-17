from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse
# Create your views here.


def profile(request):
    return HttpResponse("Hello, world. You're at the blog index.")


def log_out(request):
    logout(request)
    # return redirect(request.META.get('HTTP_REFERER'))
    return HttpResponse("You've been logged out.")