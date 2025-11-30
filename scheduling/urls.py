from django.urls import path, include
from .views import *

urlpatterns = [
     path('', home, name='home'),
     path('classes/', classes, name='classes'),
     path('member_dashboard/', member_dashboard, name='member_dashboard'),
     path('trainer_dashboard/', trainer_dashboard, name='trainer_dashboard'),
     path('staff_dashboard/', staff_dashboard, name='staff_dashboard'),

    ]
