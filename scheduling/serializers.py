from rest_framework import serializers
from .models import Group, Schedule, Booking, GroupRecord


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class GroupRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRecord
        fields = '__all__'
