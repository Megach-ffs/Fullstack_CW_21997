from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', register_member, name='register_member'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('password-change/', change_password, name='change_password'),
    ]
