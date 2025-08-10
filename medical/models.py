from django.db import models
from django.utils import timezone
from Customer.models import CustomerUser

STATES = [
    ('Maharashtra', 'Maharashtra'),
    ('Gujarat', 'Gujarat'),
    ('Delhi', 'Delhi'),
    # Add more as needed
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Delivered', 'Delivered'),
]


class MediRegistration(models.Model):

    store_name = models.CharField(max_length=150)  # ✅ Newly added

    # Owner Details
    owner_name = models.CharField(max_length=100)
    owner_photo = models.ImageField(upload_to='owner_photos/')
    owner_id_proof = models.FileField(upload_to='owner_id_proofs/')

    # Pharmacist Details
    pharmacist_name = models.CharField(max_length=100)
    pharmacist_photo = models.ImageField(upload_to='pharmacist_photos/')

    # Address Details
    address = models.TextField()
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATES)
    pincode = models.PositiveIntegerField()

    # Contact Info
    contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    shop_no = models.CharField(max_length=50)

    # License and Legal Documents
    license_no = models.CharField(max_length=100)
    license_photo = models.ImageField(upload_to='license_photos/')
    intimation_letter_photo = models.ImageField(upload_to='intimation_letters/')
    food_license_photo = models.ImageField(upload_to='food_licenses/')

    # Bank Details
    bank_account_no = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)
    passbook_photo = models.ImageField(upload_to='passbook_photos/')

    # Approval Status
    is_approved = models.BooleanField(default=False)

    # New fields for username and password
    username = models.CharField(max_length=100, unique=True)  # Ensure unique usernames
    password = models.CharField(max_length=255)  # Store password as a hash

    def __str__(self):
        return f"{self.store_name} - {self.owner_name}"




from django.db import models
from .models import MediRegistration  # adjust import if needed

class Medicine(models.Model):
    medical_store = models.ForeignKey(MediRegistration, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField()
    expiry_date = models.DateField()
    medicine_image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    prescription_required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.medical_store.store_name}"





class PrescriptionBill(models.Model):
    prescription = models.OneToOneField('Customer.Prescription', on_delete=models.CASCADE, related_name='bill')
    customer = models.ForeignKey('Customer.CustomerUser', on_delete=models.CASCADE, related_name='bills')
    medical_store = models.ForeignKey('MediRegistration', on_delete=models.CASCADE, related_name='bills')
    generated_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_notified = models.BooleanField(default=False)


    def __str__(self):
        return f"Bill #{self.id} for {self.customer.name} by {self.medical_store.store_name}"


class PrescriptionBillItem(models.Model):
    bill = models.ForeignKey(PrescriptionBill, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    mrp = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine_name} (x{self.quantity})"

    def save(self, *args, **kwargs):
        self.amount = self.mrp * self.quantity
        super().save(*args, **kwargs)

from django.db import models

ISSUE_STATUS_CHOICES = [
    ("open", "Open"),
    ("in_progress", "In Progress"),
    ("resolved", "Resolved"),
    ("closed", "Closed"),
]

class MedicalIssue(models.Model):
    store = models.ForeignKey('MediRegistration', on_delete=models.CASCADE)
    issue = models.TextField()
    status = models.CharField(max_length=20, choices=ISSUE_STATUS_CHOICES, default="open")

    def __str__(self):
        return f"Issue for {self.store.store_name}"
