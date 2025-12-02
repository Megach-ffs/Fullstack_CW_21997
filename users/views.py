from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from .forms import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
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


@login_required
def user_profile(request):
    user = request.user
    trainer_form = None

    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        
        if user.role == 'trainer':
            trainer_form = TrainerProfileUpdateForm(request.POST, instance=user.trainer)
        
        if user_form.is_valid() and (trainer_form is None or trainer_form.is_valid()):
            user_form.save()
            if trainer_form:
                trainer_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserProfileUpdateForm(instance=user)
        if user.role == 'trainer':
            trainer_form = TrainerProfileUpdateForm(instance=user.trainer)

    context = {
        'user_form': user_form,
        'trainer_form': trainer_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})




