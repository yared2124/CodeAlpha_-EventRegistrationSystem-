from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # Display these fields in the user list
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    # Add 'role' to the fieldsets in the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    # Add 'role' to the fields when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )


admin.site.register(User, CustomUserAdmin)