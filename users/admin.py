from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin

admin.site.register(Member)
admin.site.register(Staff)
admin.site.register(Trainer)

class CustomAdmin(UserAdmin):
    form = AdminChange
    add_form = AdminForm

    list_display = UserAdmin.list_display + ('role', 'phone')

    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields':('role','phone')}),
        )

    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Role', {'fields':('role','phone')}), 
    )

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


admin.site.register(User, CustomAdmin)








