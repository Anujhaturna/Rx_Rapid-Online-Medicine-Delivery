from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ManagerProfile

# Unregister User only if it's already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)

# Inline version of ManagerProfile
class ManagerProfileInline(admin.StackedInline):
    model = ManagerProfile
    can_delete = False
    verbose_name_plural = 'Manager Profile'

# Extend User admin
class CustomUserAdmin(UserAdmin):
    inlines = (ManagerProfileInline,)

admin.site.register(User, CustomUserAdmin)

# Register ManagerProfile separately (optional)
@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone_number', 'date_joined')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('date_joined',)


from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('send_to', 'medical_store', 'message', 'scheduled_date', 'created_at')

    # Filters for easy searching
    list_filter = ('send_to', 'scheduled_date')

    # Fields that can be searched
    search_fields = ('message', 'send_to', 'medical_store__name')

    # Exclude the 'created_at' field from the form since it's auto-generated
    exclude = ('created_at',)

    # Optional: You can also define fields to display in the detail page
    fields = ('send_to', 'medical_store', 'message', 'scheduled_date')  # No 'created_at' here


admin.site.register(Notification, NotificationAdmin)
