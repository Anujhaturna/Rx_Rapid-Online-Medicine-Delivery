from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomerUser, OTP, MedicineRequest, ShippingDetails


# ----------------------------
# CustomerUser Admin
# ----------------------------
class CustomerUserAdmin(UserAdmin):
    model = CustomerUser
    list_display = ['email', 'phone', 'name', 'address', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'phone', 'name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'phone', 'name', 'address', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )


admin.site.register(CustomerUser, CustomerUserAdmin)


# ----------------------------
# OTP Admin
# ----------------------------
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at', 'is_verified']
    list_filter = ['is_verified']
    search_fields = ['user__email', 'user__phone', 'code']
    ordering = ['created_at']


admin.site.register(OTP, OTPAdmin)


# ----------------------------
# Medicine Request Admin
# ----------------------------
from django.contrib import admin
from django.utils.html import format_html
from .models import MedicineRequest

class MedicineRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'name', 'description', 'image_tag']
    search_fields = ['customer__email', 'name']
    ordering = ['customer']
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'

admin.site.register(MedicineRequest, MedicineRequestAdmin)


# ----------------------------
# Shipping Details Admin
# ----------------------------
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'full_name', 'phone_number', 'address', 'city', 'email', 'medical_store']
    list_filter = ['city']
    search_fields = ['customer__email', 'full_name', 'medical_store']
    ordering = ['full_name']


admin.site.register(ShippingDetails, ShippingDetailsAdmin)


from django.contrib import admin
from .models import Reminder

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('id', 'prescription', 'remind_at', 'interval', 'is_sent')
    list_filter = ('is_sent', 'remind_at')
    search_fields = ('prescription__customer__email', 'prescription__store__store_name')
    ordering = ('-remind_at',)
    date_hierarchy = 'remind_at'


from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'medical_store',
        'total_price',
        'gst',
        'grand_total',
        'status',
        'payment_method',
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('customer__username', 'medical_store__store_name', 'status')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

# Customer/admin.py
from django.contrib import admin
from .models import CustomerIssue

@admin.register(CustomerIssue)
class CustomerIssueAdmin(admin.ModelAdmin):
    list_display = ('customer', 'subject', 'is_read', 'contact')
    list_filter = ('is_read',)
    search_fields = ('subject', 'customer__username')



from django.contrib import admin
from .models import Prescription
from django.utils.html import format_html

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'store', 'status', 'upload_time', 'preview_prescription')
    list_filter = ('status', 'upload_time', 'store')
    search_fields = ('customer__username', 'store__store_name', 'status')
    readonly_fields = ('upload_time', 'preview_prescription',)
    fieldsets = (
        ('Customer & Store Info', {
            'fields': ('customer', 'store', 'status')
        }),
        ('File Uploads', {
            'fields': ('prescription_file', 'image', 'preview_prescription',)
        }),
        ('Additional Info', {
            'fields': ('delivery_address', 'notes', 'reminder_months', 'upload_time')
        }),
    )

    def preview_prescription(self, obj):
        if obj.prescription_file:
            if obj.prescription_file.url.lower().endswith(('.jpg', '.jpeg', '.png')):
                return format_html(f'<img src="{obj.prescription_file.url}" width="100" height="100" />')
            else:
                return format_html(f'<a href="{obj.prescription_file.url}" target="_blank">Download</a>')
        return "No file"

    preview_prescription.short_description = "Prescription File Preview"



