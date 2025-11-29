from django.shortcuts import render, redirect

def home(request):
    return render(request, 'scheduling/home.html')

def member_dashboard(request):
    return render(request, 'scheduling/member_dashboard.html')

def trainer_dashboard(request):
    return render(request, 'scheduling/trainer_dashboard.html')

def classes(request):
    return render(request, 'scheduling/classes.html')

