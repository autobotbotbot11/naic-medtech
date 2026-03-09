from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "display_name", "email", "is_staff", "is_active")
    search_fields = ("username", "display_name", "email")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("display_name",)}),
    )
