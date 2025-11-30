from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.db.models import Count, Exists, OuterRef, Subquery, BooleanField, Value
from .models import *
from .forms import *
from users.models import *

def home(request):
    return render(request, 'scheduling/home.html')

@login_required
def member_dashboard(request):


    member = request.user.member

    active_records = GroupRecord.objects.filter(member=member, status='active').values_list('group_id', flat=True)

    my_classes = Schedule.objects.filter( group_id__in=active_records,
                                          status='active').order_by('start_time')
    my_bookings = Booking.objects.filter(member=member).order_by('start_time')

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            date = form.cleaned_data['date']
            time_obj = form.cleaned_data['time']

            start_date = timezone.make_aware(datetime.combine(date, time_obj))
            end_date= start_date + timedelta(hours=1)

            if Booking.objects.filter(trainer=trainer, start_time = start_date, status='active').exists():
                messages.error(request, 'Trainer is already booked for this time')
            else:
                Booking.objects.create(member=member, trainer=trainer, start_time=start_date,
                                       end_time=end_date, status='pending'
                                       )
                messages.success(request, 'You have sent a request to trainer')
                return redirect('member_dashboard')

    else:
        form = BookingForm()

    return render(request, 'scheduling/member_dashboard.html', {'my_classes':my_classes, 'my_bookings':my_bookings, 'booking_form':form})

@login_required
def trainer_dashboard(request):

    trainer = request.user.trainer
    my_schedule = Schedule.objects.filter(trainer=trainer, start_time__gte=timezone.now()).order_by('start_time')
    pending = Booking.objects.filter(trainer=trainer, status='pending').order_by('start_time')
    active = Booking.objects.filter(trainer=trainer, status='active',
                                    start_time__gte=timezone.now()).order_by('start_time')
    print(active)
    if request.method == 'POST':
        form = TrainerDecision(request.POST)
        if form.is_valid():
            booking_id = form.cleaned_data['booking_id']
            action = form.cleaned_data['action']
            booking = get_object_or_404(Booking, id=booking_id, trainer=trainer)
            booking.status = action
            booking.is_booked = (action == 'active')
            booking.save()
            messages.success(request, f"Booking {action}d")
            return redirect('trainer_dashboard')


    return render(request, 'scheduling/trainer_dashboard.html', {'my_schedule':my_schedule, 'pending':pending,
                                                                 'active':active, })

@login_required
def staff_dashboard(request):

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():

            instance = form.save(commit=False)

            start_date = form.cleaned_data['start_date']
            time_start = form.cleaned_data['time_start']
            time_end = form.cleaned_data['time_end']

            instance.start_time = timezone.make_aware(datetime.combine(start_date, time_start))
            instance.end_time = timezone.make_aware(datetime.combine(start_date, time_end))
            
            recurrences = form.cleaned_data['recurrence_days']
            if recurrences:
                instance.recurrence_days = ",".join(recurrences)

            instance.save()

            amount = 1
            if recurrences and instance.repeat_until:
                target_days = [int(x) for x in recurrences]
                tmrw = start_date + timedelta(days=1)

                while tmrw <= instance.repeat_until:
                    if tmrw.weekday() in target_days:
                        Schedule.objects.create(
                            group=instance.group,
                            trainer=instance.trainer,
                            room=instance.room,
                            status=instance.status,
                            recurrence_days=instance.recurrence_days,
                            repeat_until=instance.repeat_until,
                            start_time=timezone.make_aware(datetime.combine(tmrw, time_start)),
                            end_time=timezone.make_aware(datetime.combine(tmrw, time_end))
                            )
                        amount +=1
                    tmrw  += timedelta(days=1)
            messages.success(request, f'Created {amount} schedule sessions')
            return redirect('staff_dashboard')
    else:
        form = ScheduleForm()

    return render(request, 'scheduling/staff_dashboard.html', {'form':form})
            


@login_required
def classes(request):
    
    # Define a subquery to count the number of *active* members for each group
    # This count is independent of the Schedule join, solving the over-counting issue.
    enrollment_count_subquery = GroupRecord.objects.filter(
        group=OuterRef('pk'), 
        status='active'
    ).values('group').annotate(
        count=Count('pk')
    ).values('count')
    
    # 1. Start with the base queryset for active groups
    groups_queryset = Group.objects.filter(
        schedule__status='active', 
        schedule__start_time__gte=timezone.now()
    ).distinct()

    # 2. Add annotation for current enrollment count using the subquery
    groups_queryset = groups_queryset.annotate(
        current_enrollment=Subquery(enrollment_count_subquery)
    ).order_by('name')
    
    # 3. Add annotation for user enrollment status (only for members)
    if request.user.is_authenticated and request.user.role == 'member':
        member = request.user.member
        
        # Check if an active GroupRecord exists for the current member and group (OuterRef('pk') links back to the current Group)
        is_enrolled_subquery = GroupRecord.objects.filter(
            group=OuterRef('pk'), 
            member=member, 
            status='active'
        )
        
        groups_queryset = groups_queryset.annotate(
            is_enrolled=Exists(is_enrolled_subquery)
        )
    else:
        # If not a member/logged in, default is_enrolled to False
        groups_queryset = groups_queryset.annotate(is_enrolled=Value(False, output_field=BooleanField()))

    active_groups = groups_queryset


    if request.method == 'POST' and request.user.role =='member':
        
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id) # FIX: Look up Group, not Schedule
        member = request.user.member
        
        # Check 1: Already enrolled
        if GroupRecord.objects.filter(member=member, group=group, status='active').exists():
            messages.warning(request, f'You are already enrolled in {group.name}.')
            return redirect('classes')

        # Check 2: Class Full (Recalculate enrollment for safety)
        current_enrollment = GroupRecord.objects.filter(group=group, status='active').count()
        if current_enrollment >= group.capacity:
            messages.error(request, f'The class "{group.name}" is full.')
            return redirect('classes')

        # Enrollment successful
        # Status is set to 'active' immediately upon signup, as per standard recurring class enrollment logic
        GroupRecord.objects.create(member=member, group=group, status='active') 
        messages.success(request, f'You have successfully signed up for {group.name}.')
        return redirect('classes')


    return render(request, 'scheduling/classes.html', {'active_groups':active_groups})