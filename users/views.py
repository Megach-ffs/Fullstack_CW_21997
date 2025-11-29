from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import *

def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = MemberForm()

    return render(request, 'users/register_member.html', {'form':form})

def user_login(request):
    
    if request.method == 'POST':
        form = UserLogin(request=request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request,'You have logged in')
            return redirect('home')
    else:
        form = UserLogin()
    return render(request, 'users/login.html',{'form':form})

def user_logout(request):
    logout(request)
    messages.info(request,'User logout')
    return redirect('home')

def user_profile(request):
    return render(request, 'users/profile.html')




