from django.db import models
from django.conf import settings

class Group(models.Model):
    name=models.CharField(max_length=50)
    description=models.TextField(blank=True)
    duration=models.IntegerField()
    capacity=models.IntegerField(default=20)

    def __str__(self):
        return self.name

class Schedule(models.Model):

    STATUS=[
        ('active','Active'),
        ('in_progress','In Progress'),
        ('inactive','Inactive'),
            ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    trainer = models.ForeignKey('users.Trainer', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.IntegerField()
    status = models.CharField(max_length=25, choices=STATUS, default='inactive')
    recurrence_days = models.CharField(max_length=50, blank=True, null=True, help_text="0=Monday, 6=Sunday") 
    repeat_until = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} - {self.start_time} - {self.trainer.user.first_name}"

class Booking(models.Model):

    STATUS=[
        ('active','Active'),
        ('pending','PEnding'),
        ('inactive','InActive'),
        ]

    member = models.ForeignKey('users.Member', on_delete=models.CASCADE)
    trainer = models.ForeignKey('users.Trainer', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default = 'pending')

    def __str__(self):
        return f"{self.trainer.user.first_name} - {self.member.user.first_name} - {self.start_time}"

class GroupRecord(models.Model):

    STATUS=[
        ('active','Active'),
        ('pending','PEnding'),
        ('inactive','InActive'),
        ('suspended','Suspended'),
        ('canceled','Canceled'),
        ]

    member = models.ForeignKey('users.Member', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='inactive')

    def __str__(self):
        return f"{self.member.user.first_name} - {self.schedule.group.name} - {self.status}"




