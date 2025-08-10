from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings


# Custom user manager
class CustomerUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone number is required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone, password, **extra_fields)


# Custom user model
class CustomerUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomerUserManager()

    def __str__(self):
        return self.email


# OTP Model
class OTP(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 300  # 5 minutes

# Prescription Model
from medical.models import MediRegistration

from django.db import models
from django.utils import timezone


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
    ]
    customer = models.ForeignKey('CustomerUser', on_delete=models.CASCADE)
    store = models.ForeignKey(MediRegistration, on_delete=models.CASCADE)
    prescription_file = models.FileField(upload_to='prescriptions/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    upload_time = models.DateTimeField(default=timezone.now)

    # ✅ Add these fields if needed:
    delivery_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reminder_months = models.PositiveIntegerField(null=True, blank=True)



    def __str__(self):
        return f"Prescription for {self.customer} at {self.store}"



# Medicine Request

# Medicine Request Model
from django.db import models
from django.utils.html import format_html

class MedicineRequest(models.Model):
    customer = models.ForeignKey('CustomerUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='medicine_requests/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - Requested by {self.customer}"

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', self.image.url)
        return "No Image"
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True  # optional, not needed in newer Django



# Shipping Details
class ShippingDetails(models.Model):
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50, default="Amravati")
    email = models.EmailField()
    medical_store = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
from medical.models import Medicine

class CartItem(models.Model):
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='items')

    def total_price(self):
        return self.medicine.price * self.quantity

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

# Order Model
from django.db import models
from django.conf import settings
from medical.models import MediRegistration, Medicine

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Delivered', 'Delivered'),
]

class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medical_store = models.ForeignKey(MediRegistration, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)  # SET_NULL instead of CASCADE to preserve order data even if medicine is deleted
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, default='cod')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.name if hasattr(self.customer, 'name') else self.customer.email}"



class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_status}"


class Invoice(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medical_store = models.ForeignKey(MediRegistration, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.email}"


class Reminder(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='reminders')
    remind_at = models.DateTimeField()  # The time when the reminder should be triggered
    interval = models.PositiveIntegerField(default=None)  # Interval in months (1 month, 2 months, etc.)
    is_sent = models.BooleanField()

    def _str_(self):
        return f"Reminder for {self.prescription.customer.email} on {self.remind_at.strftime('%Y-%m-%d %H:%M')}"

    def send_reminder(self):
        if not self.is_sent and self.remind_at <= timezone.now():
            send_mail(
                'Reminder: Medicine Refill Due',
                f"Dear {self.prescription.customer.name},\n\nYour medicine refill reminder for {self.prescription.store.store_name} is due. Please visit the store for your refill.",
                'internhimanshu3@gmail.com',
                [self.prescription.customer.email],
                fail_silently=False,
            )
            self.is_sent = True
            self.save()
            return True
        return False

    def set_next_reminder(self):
        self.remind_at = timezone.now() + timedelta(days=self.interval * 30)
        self.is_sent = False
        self.save()

# from Manager.models import User

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Delivered', 'Delivered'),
]
# Customer/models.py
from django.db import models
from django.conf import settings

class CustomerIssue(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    contact = models.CharField(max_length=15, null=True, blank=True)  # Better for phone numbers
    is_read = models.BooleanField(default=False)  # Manager will update this!

    def __str__(self):
        return f"{self.customer.username} - {self.subject}"


