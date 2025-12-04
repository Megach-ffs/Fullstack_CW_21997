from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Group, Schedule, Booking, GroupRecord
from .serializers import GroupSerializer, ScheduleSerializer, BookingSerializer, GroupRecordSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'staff'


class IsOwnerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'staff':
            return True
        if hasattr(obj, 'member'):
            return obj.member.user == request.user or obj.trainer.user == request.user
        return False


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['capacity']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'capacity', 'duration']
    ordering = ['name']


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'trainer', 'group', 'room']
    search_fields = ['group__name', 'trainer__user__first_name', 'trainer__user__last_name']
    ordering_fields = ['start_time', 'end_time', 'status']
    ordering = ['-start_time']


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'trainer', 'member', 'is_booked']
    search_fields = ['member__user__first_name', 'member__user__last_name', 
                     'trainer__user__first_name', 'trainer__user__last_name']
    ordering_fields = ['start_time', 'end_time', 'status']
    ordering = ['-start_time']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'staff':
            return Booking.objects.all()
        elif user.role == 'trainer':
            return Booking.objects.filter(trainer__user=user)
        elif user.role == 'member':
            return Booking.objects.filter(member__user=user)
        return Booking.objects.none()


class GroupRecordViewSet(viewsets.ModelViewSet):
    queryset = GroupRecord.objects.all()
    serializer_class = GroupRecordSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'group', 'member']
    search_fields = ['member__user__first_name', 'member__user__last_name', 'group__name']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'staff':
            return GroupRecord.objects.all()
        elif user.role == 'member':
            return GroupRecord.objects.filter(member__user=user)
        return GroupRecord.objects.none()
    