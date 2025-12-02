from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.db.models import Count, Exists, OuterRef, Subquery, BooleanField, Value, Q
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
    
    enrollment_count_subquery = GroupRecord.objects.filter(
        group=OuterRef('pk'), 
        # status='active'
    ).values('group').annotate(
        count=Count('pk')
    ).values('count')
    
    groups_queryset = Group.objects.filter(
        # schedule__status='active', 
        schedule__start_time__gte=timezone.now()
    ).distinct()

    
    query = request.GET.get('q')
    if query:
        groups_queryset = groups_queryset.filter(name__icontains=query)

    groups_queryset = groups_queryset.annotate(
        current_enrollment=Subquery(enrollment_count_subquery)
    ).order_by('name')
    
    if request.user.is_authenticated and request.user.role == 'member':
        member = request.user.member
        
        is_enrolled_subquery = GroupRecord.objects.filter(
            group=OuterRef('pk'), 
            member=member, 
            # status='active'
        )
        
        groups_queryset = groups_queryset.annotate(
            is_enrolled=Exists(is_enrolled_subquery)
        )
    else:
        groups_queryset = groups_queryset.annotate(is_enrolled=Value(False, output_field=BooleanField()))

    active_groups = groups_queryset


    if request.method == 'POST' and request.user.role =='member':
        
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id) 
        member = request.user.member
        
        if GroupRecord.objects.filter(member=member, group=group, status='active').exists():
            messages.warning(request, f'You are already enrolled in {group.name}.')
            return redirect('classes')
        current_enrollment = GroupRecord.objects.filter(group=group, status='active').count()
        if current_enrollment >= group.capacity:
            messages.error(request, f'The class "{group.name}" is full.')
            return redirect('classes')

        GroupRecord.objects.create(member=member, group=group, status='active') 
        messages.success(request, f'You have successfully signed up for {group.name}.')
        return redirect('classes')


    return render(request, 'scheduling/classes.html', {'active_groups':active_groups})

@login_required
def update_booking(request, booking_id):
    if request.user.role != 'trainer':
        messages.error(request, "Access denied")
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id, trainer=request.user.trainer)
    
    if request.method == 'POST':
        form = BookingTimeUpdateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_obj = form.cleaned_data['time']
            start_date = timezone.make_aware(datetime.combine(date, time_obj))
            end_date = start_date + timedelta(hours=1)
            
            if Booking.objects.filter(trainer=booking.trainer, start_time=start_date, status='active').exclude(id=booking.id).exists():
                 messages.error(request, 'You are already booked for this time')
            else:
                booking.start_time = start_date
                booking.end_time = end_date
                booking.save()
                messages.success(request, "Booking time updated successfully")
                return redirect('trainer_dashboard')
    else:
        initial_data = {
            'date': booking.start_time.date(),
            'time': booking.start_time.time()
        }
        form = BookingTimeUpdateForm(initial=initial_data)
    
    return render(request, 'scheduling/update_booking.html', {'form': form, 'booking': booking})



@login_required
def staff_trainer_list(request):
    if request.user.role != 'staff': return redirect('home')
    trainers = Trainer.objects.all()
    
    query = request.GET.get('q')
    if query:
        trainers = trainers.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(specialization__icontains=query)
        )
        
    return render(request, 'scheduling/staff/trainer_list.html', {'trainers': trainers})

@login_required
def staff_trainer_create(request):
    if request.user.role != 'staff': return redirect('home')
    if request.method == 'POST':
        form = TrainerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer created successfully")
            return redirect('staff_trainer_list')
    else:
        form = TrainerForm()
    return render(request, 'scheduling/staff/trainer_form.html', {'form': form, 'title': 'Create Trainer'})

@login_required
def staff_trainer_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    trainer = get_object_or_404(Trainer, pk=pk)
    if request.method == 'POST':
        trainer.specialization = request.POST.get('specialization')
        trainer.bio = request.POST.get('bio')
        trainer.user.first_name = request.POST.get('first_name')
        trainer.user.last_name = request.POST.get('last_name')
        trainer.user.email = request.POST.get('email')
        trainer.user.save()
        trainer.save()
        messages.success(request, "Trainer updated")
        return redirect('staff_trainer_list')

    return render(request, 'scheduling/staff/trainer_form.html', {'trainer': trainer, 'title': 'Update Trainer'})

@login_required
def staff_member_list(request):
    if request.user.role != 'staff': return redirect('home')
    members = Member.objects.all()
    
    query = request.GET.get('q')
    if query:
        members = members.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
        
    return render(request, 'scheduling/staff/member_list.html', {'members': members})

@login_required
def staff_member_create(request):
    if request.user.role != 'staff': return redirect('home')
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Member created successfully")
            return redirect('staff_member_list')
    else:
        form = MemberForm()
    return render(request, 'scheduling/staff/member_form.html', {'form': form, 'title': 'Create Member'})

@login_required
def staff_member_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.user.first_name = request.POST.get('first_name')
        member.user.last_name = request.POST.get('last_name')
        member.user.email = request.POST.get('email')
        member.user.save()
        messages.success(request, "Member updated")
        return redirect('staff_member_list')
    return render(request, 'scheduling/staff/member_form.html', {'member': member, 'title': 'Update Member'})

@login_required
def staff_group_list(request):
    if request.user.role != 'staff': return redirect('home')
    groups = Group.objects.all()
    
    query = request.GET.get('q')
    if query:
        groups = groups.filter(name__icontains=query)
        
    return render(request, 'scheduling/staff/group_list.html', {'groups': groups})

@login_required
def staff_group_create(request):
    if request.user.role != 'staff': return redirect('home')
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Group created")
            return redirect('staff_group_list')
    else:
        form = GroupForm()
    return render(request, 'scheduling/staff/group_form.html', {'form': form, 'title': 'Create Group'})

@login_required
def staff_group_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated")
            return redirect('staff_group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'scheduling/staff/group_form.html', {'form': form, 'title': 'Update Group'})

@login_required
def staff_schedule_list(request):
    if request.user.role != 'staff': return redirect('home')
    schedules = Schedule.objects.all().order_by('-start_time')
    
    query = request.GET.get('q')
    status = request.GET.get('status')
    
    if query:
        schedules = schedules.filter(group__name__icontains=query)
    if status:
        schedules = schedules.filter(status=status)
        
    return render(request, 'scheduling/staff/schedule_list.html', {'schedules': schedules})

@login_required
def staff_schedule_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.room = request.POST.get('room')
        schedule.status = request.POST.get('status')
        schedule.save()
        messages.success(request, "Schedule updated")
        return redirect('staff_schedule_list')
    return render(request, 'scheduling/staff/schedule_form.html', {'schedule': schedule, 'title': 'Update Schedule'})
@login_required
def staff_booking_list(request):
    if request.user.role != 'staff': return redirect('home')
    bookings = Booking.objects.all().order_by('-start_time')
    
    query = request.GET.get('q')
    status = request.GET.get('status')
    
    if query:
        bookings = bookings.filter(
            Q(trainer__user__first_name__icontains=query) |
            Q(member__user__first_name__icontains=query)
        )
    if status:
        bookings = bookings.filter(status=status)
        
    return render(request, 'scheduling/staff/booking_list.html', {'bookings': bookings})

@login_required
def staff_booking_create(request):
    if request.user.role != 'staff': return redirect('home')
    if request.method == 'POST':
        form = StaffBookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking created")
            return redirect('staff_booking_list')
    else:
        form = StaffBookingForm()
    return render(request, 'scheduling/staff/booking_form.html', {'form': form, 'title': 'Create Booking'})

@login_required
def staff_booking_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = StaffBookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated")
            return redirect('staff_booking_list')
    else:
        form = StaffBookingForm(instance=booking)
    return render(request, 'scheduling/staff/booking_form.html', {'form': form, 'title': 'Update Booking'})
@login_required
def staff_grouprecord_list(request):
    if request.user.role != 'staff': return redirect('home')
    records = GroupRecord.objects.all()
    
    status = request.GET.get('status')
    if status:
        records = records.filter(status=status)
        
    return render(request, 'scheduling/staff/grouprecord_list.html', {'records': records})

@login_required
def staff_grouprecord_create(request):
    if request.user.role != 'staff': return redirect('home')
    if request.method == 'POST':
        form = GroupRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Record created")
            return redirect('staff_grouprecord_list')
    else:
        form = GroupRecordForm()
    return render(request, 'scheduling/staff/grouprecord_form.html', {'form': form, 'title': 'Create Record'})

@login_required
def staff_grouprecord_update(request, pk):
    if request.user.role != 'staff': return redirect('home')
    record = get_object_or_404(GroupRecord, pk=pk)
    if request.method == 'POST':
        form = GroupRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record updated")
            return redirect('staff_grouprecord_list')
    else:
        form = GroupRecordForm(instance=record)
    return render(request, 'scheduling/staff/grouprecord_form.html', {'form': form, 'title': 'Update Record'})