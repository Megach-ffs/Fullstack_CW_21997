from django.urls import path, include
from .views import *

urlpatterns = [
     path('', home, name='home'),
     path('classes/', classes, name='classes'),
     path('member_dashboard/', member_dashboard, name='member_dashboard'),
     path('trainer_dashboard/', trainer_dashboard, name='trainer_dashboard'),
     path('staff_dashboard/', staff_dashboard, name='staff_dashboard'),

     path('booking/update/<int:booking_id>/', update_booking, name='update_booking'),

     path('staff/trainers/', staff_trainer_list, name='staff_trainer_list'),
     path('staff/trainers/create/', staff_trainer_create, name='staff_trainer_create'),
     path('staff/trainers/update/<int:pk>/', staff_trainer_update, name='staff_trainer_update'),

     path('staff/members/', staff_member_list, name='staff_member_list'),
     path('staff/members/create/', staff_member_create, name='staff_member_create'),
     path('staff/members/update/<int:pk>/', staff_member_update, name='staff_member_update'),

     path('staff/groups/', staff_group_list, name='staff_group_list'),
     path('staff/groups/create/', staff_group_create, name='staff_group_create'),
     path('staff/groups/update/<int:pk>/', staff_group_update, name='staff_group_update'),

     path('staff/schedules/', staff_schedule_list, name='staff_schedule_list'),
     path('staff/schedules/update/<int:pk>/', staff_schedule_update, name='staff_schedule_update'),

     path('staff/bookings/', staff_booking_list, name='staff_booking_list'),
     path('staff/bookings/create/', staff_booking_create, name='staff_booking_create'),
     path('staff/bookings/update/<int:pk>/', staff_booking_update, name='staff_booking_update'),

     path('staff/records/', staff_grouprecord_list, name='staff_grouprecord_list'),
     path('staff/records/create/', staff_grouprecord_create, name='staff_grouprecord_create'),
     path('staff/records/update/<int:pk>/', staff_grouprecord_update, name='staff_grouprecord_update'),

    ]
