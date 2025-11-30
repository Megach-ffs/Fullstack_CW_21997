from django.forms import (ModelForm, DateField, TimeField, TimeInput, DateInput,
                          MultipleChoiceField, CheckboxSelectMultiple, ValidationError,
                          ModelChoiceField,Form, ChoiceField, IntegerField, RadioSelect, HiddenInput)
from .models import *
from django.utils import timezone
from users.models import Trainer

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
    start_date = DateField(widget=DateInput(attrs={'type':'date'}), label='Starting day')
    time_start = TimeField(widget=TimeInput(attrs={'type':'time'}), label='Starting time')
    time_end = TimeField(widget=TimeInput(attrs={'type':'time'}),label='Ending time')

    class Meta:
        model = Schedule
        fields = ['group', 'trainer', 'room', 'status', 'repeat_until', 'recurrence_days']
        widgets = {
                'repeat_until':DateInput(attrs={'type':'date'})
                }


    def clean(self):
        cleaned_data = super().clean()
        recurrence = cleaned_data.get('recurrence_days')
        until = cleaned_data.get('repeat_until')

        if recurrence and not until:
            raise ValidationError("Pick repeat util")
        return cleaned_data


class BookingForm(ModelForm):

    trainer = ModelChoiceField(queryset=Trainer.objects.all())
    date = DateField(widget=DateInput(attrs={'type':'date'}))
    time = TimeField(widget=TimeInput(attrs={'type':'time'}))

    class Meta:
        model = Booking
        fields = ['trainer', 'date','time']

class GroupSignupForm(Form):
    
    group_id = IntegerField(widget=HiddenInput)
    
class TrainerDecision(Form):

    ACTION_CH = [('active','Accept'),('inactive','Decline')]
    action = ChoiceField(choices=ACTION_CH, widget=RadioSelect)
    booking_id = IntegerField(widget=HiddenInput)



