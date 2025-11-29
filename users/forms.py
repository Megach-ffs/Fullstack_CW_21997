from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.db import transaction
from .models import *

class UserForm(UserCreationForm):

    phone = forms.CharField(max_length=12, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone', 'first_name','last_name','email')

class MemberForm(UserForm):

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        user.role = 'member'
        user.email = self.cleaned_data.get('email')
        user.save()

        Member.objects.create(user=user)
        return user

class TrainerForm(UserForm):

    specialization = forms.CharField(max_length=50)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        user.role = 'trainer'
        user.email = self.cleaned_data.get('email')
        user.save()

        Trainer.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                bio = self.cleaned_data.get('bio'),
                )
        return user

class UserLogin(AuthenticationForm):
    pass

class AdminForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User

        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'role', 'phone',        
            ) 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AdminChange(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active',
            'is_staff', 'is_superuser', 'groups', 'user_permissions', 
            'role', 'phone', 
            )




