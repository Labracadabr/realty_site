from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "is_active", "last_login")
    fieldsets = BaseUserAdmin.fieldsets + (("Contacts & notifications", {"fields": ("phone", "telegram_chat_id")}),)

    @admin.display(description="Role")
    def role(self, obj):
        if obj.is_superuser:
            return "Admin"
        if obj.is_partner:
            return "Partner"
        return "Staff" if obj.is_staff else "—"
