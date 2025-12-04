from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views_api import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'members', MemberViewSet)
router.register(r'trainers', TrainerViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path('register/', register_member, name='register_member'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('password-change/', change_password, name='change_password'),
    path('api/', include(router.urls)),
]
