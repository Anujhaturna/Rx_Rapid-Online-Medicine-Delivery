from django.contrib import admin
from .models import (
    MediRegistration,
    Medicine,
    PrescriptionBill,
    PrescriptionBillItem
)


@admin.register(MediRegistration)
class MediRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'store_name', 'owner_name', 'pharmacist_name', 'email',
        'contact', 'city', 'state', 'is_approved'
    )
    list_filter = ('state', 'is_approved')
    search_fields = ('store_name', 'owner_name', 'email', 'license_no', 'username')

    fieldsets = (
        ('Store Information', {
            'fields': ('store_name',)
        }),
        ('Owner Details', {
            'fields': ('owner_name', 'owner_photo', 'owner_id_proof')
        }),
        ('Pharmacist Details', {
            'fields': ('pharmacist_name', 'pharmacist_photo')
        }),
        ('Address Details', {
            'fields': ('address', 'street_address', 'city', 'state', 'pincode')
        }),
        ('Contact Information', {
            'fields': ('contact', 'email', 'shop_no')
        }),
        ('License and Legal Documents', {
            'fields': ('license_no', 'license_photo', 'intimation_letter_photo', 'food_license_photo')
        }),
        ('Bank Details', {
            'fields': ('bank_account_no', 'ifsc_code', 'passbook_photo')
        }),
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Approval', {
            'fields': ('is_approved',)
        }),
    )



from django.contrib import admin
from django.utils.html import format_html
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'medical_store',
        'brand',
        'price',
        'quantity_in_stock',
        'expiry_date',
        'created_at',
        'medicine_image_preview',
    )
    list_filter = ('medical_store', 'brand', 'expiry_date', 'created_at')
    search_fields = ('name', 'brand', 'medical_store__store_name')
    readonly_fields = ('created_at', 'medicine_image_preview')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'medical_store',
                'name',
                'brand',
                'description',
                ('price', 'quantity_in_stock'),
                'expiry_date',
                'medicine_image',
                'medicine_image_preview',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

    def medicine_image_preview(self, obj):
        if obj.medicine_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                               obj.medicine_image.url)
        return "No Image"

    medicine_image_preview.short_description = 'Medicine Image Preview'


@admin.register(PrescriptionBill)
class PrescriptionBillAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'prescription', 'customer', 'medical_store',
        'generated_at', 'total_amount', 'is_notified'
    )
    list_filter = ('medical_store', 'generated_at', 'is_notified')
    search_fields = (
        'patient__username', 'customer__email',
        'medical_store__store_name', 'prescription__id'
    )

    fieldsets = (
        ('Bill Details', {
            'fields': (
                'prescription', 'customer', 'medical_store',
                'generated_at', 'total_amount', 'is_notified'
            )
        }),
    )
    readonly_fields = ('generated_at',)


@admin.register(PrescriptionBillItem)
class PrescriptionBillItemAdmin(admin.ModelAdmin):
    list_display = (
        'bill', 'medicine_name', 'batch_number',
        'expiry_date', 'mrp', 'quantity', 'amount'
    )
    list_filter = ('expiry_date',)
    search_fields = ('medicine_name', 'batch_number', 'bill__id')

    fieldsets = (
        ('Bill Item Details', {
            'fields': (
                'bill', 'medicine_name', 'batch_number',
                'expiry_date', 'mrp', 'quantity', 'amount'
            )
        }),
    )

from django.contrib import admin
from .models import MedicalIssue

@admin.register(MedicalIssue)
class MedicalIssueAdmin(admin.ModelAdmin):
    list_display = ('store', 'issue', 'status')
    list_filter = ('status',)
    search_fields = ('store__store_name',)

