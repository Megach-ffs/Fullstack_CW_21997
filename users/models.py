from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    ROLES = [
        ('member', 'Member'),
        ('trainer', 'Trainer'),
        ('staff', 'Staff'),
    ]

    role = models.CharField(max_length=10, choices=ROLES, default='member')
    phone = models.CharField(max_length=12, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role} - {self.first_name} - {self.last_name}"

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialization = models.CharField(max_length=50)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name}"

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name}"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name}"






