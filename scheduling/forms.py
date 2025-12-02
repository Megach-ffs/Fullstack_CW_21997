from django.forms import (ModelForm, DateField, TimeField, TimeInput, DateInput,
                          MultipleChoiceField, CheckboxSelectMultiple, ValidationError,
                          ModelChoiceField,Form, ChoiceField, IntegerField, RadioSelect, HiddenInput,
                          Select, NumberInput, TextInput, Textarea, DateTimeInput, CheckboxInput)
from .models import *
from django.utils import timezone
from users.models import Trainer, Member
from users.forms import MemberForm, TrainerForm 

class ScheduleForm(ModelForm):

    WEEKDAYS = [
        ('0', 'Monday'),
        ('1', 'Tuesdau'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ]

    recurrence_days = MultipleChoiceField(
        choices = WEEKDAYS,
        widget=CheckboxSelectMultiple,
        required=False,
        label='Repeating days'
        )
    start_date = DateField(widget=DateInput(attrs={'type':'date', 'class': 'form-control'}), label='Starting day')
    time_start = TimeField(widget=TimeInput(attrs={'type':'time', 'class': 'form-control'}), label='Starting time')
    time_end = TimeField(widget=TimeInput(attrs={'type':'time', 'class': 'form-control'}),label='Ending time')

    class Meta:
        model = Schedule
        fields = ['group', 'trainer', 'room', 'status', 'repeat_until', 'recurrence_days']
        widgets = {
                'repeat_until':DateInput(attrs={'type':'date', 'class': 'form-control'}),
                'group': Select(attrs={'class': 'form-select'}),
                'trainer': Select(attrs={'class': 'form-select'}),
                'room': NumberInput(attrs={'class': 'form-control'}),
                'status': Select(attrs={'class': 'form-select'}),
                }


    def clean(self):
        cleaned_data = super().clean()
        recurrence = cleaned_data.get('recurrence_days')
        until = cleaned_data.get('repeat_until')

        if recurrence and not until:
            raise ValidationError("Pick repeat util")
        return cleaned_data


class BookingForm(ModelForm):

    trainer = ModelChoiceField(queryset=Trainer.objects.all(), widget=Select(attrs={'class': 'form-select'}))
    date = DateField(widget=DateInput(attrs={'type':'date', 'class': 'form-control'}))
    time = TimeField(widget=TimeInput(attrs={'type':'time', 'class': 'form-control'}))

    class Meta:
        model = Booking
        fields = ['trainer', 'date','time']

class GroupSignupForm(Form):
    
    group_id = IntegerField(widget=HiddenInput)
    
class TrainerDecision(Form):

    ACTION_CH = [('active','Accept'),('inactive','Decline')]
    action = ChoiceField(choices=ACTION_CH, widget=RadioSelect)
    booking_id = IntegerField(widget=HiddenInput)


class BookingTimeUpdateForm(ModelForm):
    date = DateField(widget=DateInput(attrs={'type':'date', 'class': 'form-control'}))
    time = TimeField(widget=TimeInput(attrs={'type':'time', 'class': 'form-control'}))

    class Meta:
        model = Booking
        fields = ['date', 'time']

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration': NumberInput(attrs={'class': 'form-control'}),
            'capacity': NumberInput(attrs={'class': 'form-control'}),
        }

class GroupRecordForm(ModelForm):
    class Meta:
        model = GroupRecord
        fields = '__all__'
        widgets = {
            'member': Select(attrs={'class': 'form-select'}),
            'group': Select(attrs={'class': 'form-select'}),
            'status': Select(attrs={'class': 'form-select'}),
        }

class StaffBookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'member': Select(attrs={'class': 'form-select'}),
            'trainer': Select(attrs={'class': 'form-select'}),
            'start_time': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': Select(attrs={'class': 'form-select'}),
            'is_booked': CheckboxInput(attrs={'class': 'form-check-input'}),
        }




