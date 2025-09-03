from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'role', 'phone_number', 'company_name', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    # Fields for editing/creating users in admin
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone_number', 'company_name')}),
    )

    # Fields when creating a new user in admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'phone_number', 'company_name')}),
    )

    search_fields = ('username', 'email', 'phone_number', 'company_name')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
