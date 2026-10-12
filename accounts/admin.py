from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "is_staff", "is_active", "last_login")
    fieldsets = BaseUserAdmin.fieldsets + (("Contacts & notifications", {"fields": ("phone", "telegram_chat_id")}),)

    @admin.display(description="Role")
    def role(self, obj):
        if obj.is_superuser:
            return "Admin"
        if obj.is_partner:
            return "Partner"
        return "Staff" if obj.is_staff else "—"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # The admin login only admits is_staff users; admins and partners always need it.
        user = form.instance
        if not user.is_staff and (user.is_superuser or user.is_partner):
            user.is_staff = True
            user.save(update_fields=["is_staff"])
            messages.info(request, f"“Staff status” was enabled for {user} so they can log in to the admin.")
