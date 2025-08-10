import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q


from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import random
from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Prescription
from django.contrib.auth.decorators import login_required
from .models import Prescription
from .forms import ProfileForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Prescription
from .models import  Order# Assuming Order is in the same app
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from medical.models import Medicine, MediRegistration
from .models import CustomerUser  # If you’re using a custom user model
# from .models import CartItem  # Assuming CartItem is defined
from .models import  MedicineRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CartItem  # Make sure you import this
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from decimal import Decimal
from .models import CartItem, ShippingDetails
from .forms import ShippingDetailsForm
from medical.models import  MediRegistration






def index(request):
    template = loader.get_template('Customer/first_home.html')
    return HttpResponse(template.render())



# Generate a 6-digit numeric OTP
def generate_otp():
    return str(random.randint(100000, 999999))


def resend_otp_view(request):
    # Retrieve email from session
    email = request.session.get('temp_email')

    if not email:
        return redirect('home')  # If no email in session, redirect to the home page

    # Generate a new OTP
    otp_code = generate_otp()

    # Store the new OTP in session
    request.session['otp'] = otp_code

    # Send the new OTP to the email
    try:
        send_mail(
            'RxRapid OTP Verification',
            f'Your new OTP for RxRapid registration is: {otp_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
        messages.info(request, 'OTP has been resent to your email.')
    except Exception as e:
        messages.error(request, 'Failed to resend OTP. Please try again.')

    return redirect('verify-otp')  # Redirect back to OTP verification page

def verify_otp(request):
    # Check if email exists in the session
    email = request.session.get('temp_email')

    if not email:
        messages.error(request, 'Session expired. Please request OTP again.')
        return redirect('login')  # Redirect to login page

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        generated_otp = request.session.get('otp')

        if otp_input == generated_otp:
            # Get the user and log them in
            user_model = get_user_model()
            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:
                messages.error(request, 'User not found. Please register first.')
                return redirect('register')  # Redirect to registration page

            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Set backend for login
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('customer-dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'customer/verify_otp.html', {'otp': request.session.get('otp')})





# Home page view
def home_view(request):
    return render(request, 'customer/home.html')


# Step 1 - Email input
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['temp_email'] = email  # Store email in the session

        # Generate OTP and send email immediately
        otp = generate_otp()
        request.session['otp'] = otp  # Store OTP in session

        try:
            send_mail(
                'RxRapid OTP Verification',
                f'Your OTP for RxRapid registration is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.info(request, 'OTP sent to your email.')
        except Exception as e:
            messages.error(request, 'Failed to send OTP. Try again.')

        return redirect('create-account')  # Redirect to create-account page

    return render(request, 'customer/register.html')


def create_account(request):
    email = request.session.get('temp_email')
    if not email:
        return redirect('home_view')

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        otp_input = request.POST.get('otp')
        generated_otp = request.session.get('otp')

        if not name or not phone:
            messages.error(request, 'Name and phone number are required.')
            return render(request, 'customer/create_account.html', {'email': email})

        if otp_input:
            if otp_input == generated_otp:
                # Check if user already exists
                user, created = CustomerUser.objects.get_or_create(email=email)

                if not created:
                    # User already exists, update details
                    user.name = name
                    user.phone = phone
                    user.address = address
                    user.save()
                else:
                    user.name = name
                    user.phone = phone
                    user.address = address
                    user.save()

                # ✅ Log the user in
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                messages.success(request, 'Account created successfully!')
                return redirect('customer-dashboard')
            else:
                messages.error(request, 'Invalid OTP')
        else:
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            try:
                send_mail(
                    'RxRapid OTP Verification',
                    f'Your OTP for RxRapid registration is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )
                messages.info(request, 'OTP sent to your email.')
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Try again.')

    return render(request, 'Customer/create_account.html', {'email': email})


# Customer Dashboard after login
@login_required
def customer_dashboard(request):
    return render(request, 'Customer/customer_dashboard.html')


# Start Registration Page
def start_registration(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['temp_email'] = email  # Store email in the session
        return redirect('create-account')
    return render(request, 'customer/start_registration.html')


# Resend OTP


# Create the login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if email is registered
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            messages.error(request, 'Email not registered. Please sign up.')
            return redirect('register')  # Redirect to registration page

        # Generate OTP and send to email
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp  # Store OTP in session
        request.session['temp_email'] = email  # Store email temporarily for the next step

        # Send OTP to the user's email
        try:
            send_mail(
                'RxRapid OTP Verification',
                f'Your OTP for RxRapid login is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.info(request, 'OTP sent to your email.')
            return redirect('verify-otp')  # Redirect to OTP verification page
        except Exception as e:
            messages.error(request, 'Failed to send OTP. Try again.')
            return redirect('login')

    return render(request, 'customer/login.html')







from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from medical.models import Medicine, MediRegistration
from .forms import ProfileForm
from django.http import JsonResponse
from .models import  Prescription

# ----------------------------
# Upload Prescription View
# ----------------------------
  # Make sure this import exists

from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Reminder




@login_required
def upload_prescription(request):
    stores = MediRegistration.objects.all()

    if request.method == 'POST':
        prescription_file = request.FILES.get('prescription')
        store_id = request.POST.get('store')
        delivery_address = request.POST.get('address')
        notes = request.POST.get('notes')
        reminder_months = request.POST.get('reminder_months')

        if prescription_file and store_id:
            prescription = Prescription.objects.create(
                customer=request.user,
                store_id=store_id,
                prescription_file=prescription_file,
                status='pending',
                delivery_address=delivery_address,
                notes=notes,
                reminder_months=reminder_months or None
            )

            # Send reminder immediately and create Reminder object
            if reminder_months:
                remind_date = timezone.now() + timedelta(days=int(reminder_months) * 30)

                Reminder.objects.create(
                    prescription=prescription,
                    remind_at=remind_date,
                    interval=int(reminder_months),
                    is_sent=True  # Already sending now
                )

                # Send email to medical store
                store_email = prescription.store.email
                send_mail(
                    'Reminder Set: Future Medicine Refill',
                    f"Dear {prescription.store.store_name},\n\nThe customer {prescription.customer.name} has set a medicine refill reminder for {reminder_months} month(s). Please take note.",
                    'internhimanshu3@gmail.com',
                    [store_email],
                    fail_silently=False,
                )

            messages.success(request,
                             "Prescription uploaded successfully! You’ll receive the bill shortly.")
            return redirect('upload-prescription-confirm')
        else:
            messages.error(request, "Please upload a file and select a store.")

    return render(request, 'Customer/upload_prescription.html', {
        'stores': stores,
        'user': request.user,
    })



# ----------------------------
# Profile View
# ----------------------------

@login_required
def profile(request):
    user = request.user

    # Handle form submission
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect after saving to avoid resubmission
    else:
        form = ProfileForm(instance=user)

    # Get prescription history
    prescriptions = Prescription.objects.filter(customer=user).order_by('-upload_time')

    # Get order history
    orders = Order.objects.filter(customer=user).order_by('-created_at')
    return render(request, 'Customer/profile.html', {
        'form': form,
        'prescriptions': prescriptions,
        'orders': orders,
     # Include orders in context
    })


# Medicines View
# ----------------------------
def medicines_view(request):
    medicines = Medicine.objects.all()  # Fetch all medicines (ensure Medicine model is correct)
    return render(request, 'customer/medicines.html', {'medicines': medicines})


# ----------------------------
# Search Medical Stores View
# ----------------------------

from django.db.models import Q
from medical.models import MediRegistration


def search_medical_stores(request):
    query = request.GET.get('q', '').strip()

    results = MediRegistration.objects.filter(
        Q(store_name__icontains=query) |
        Q(address__icontains=query) |
        Q(city__icontains=query) |
        Q(pincode__icontains=query)
    )[:10]  # Limit to top 10 results for performance

    stores = [
        {
            "id": store.id,
            "store_name": store.store_name,
            "address": store.address,
        }
        for store in results
    ]
    return JsonResponse({'stores': stores})





# ------------------------
# Browse Non-Prescription Medicines View
# ------------------------
@login_required
def browse_non_prescription(request, store_id=None):
    query = request.GET.get('q')
    if query:
        stores = MediRegistration.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )
    else:
        stores = MediRegistration.objects.all()

    medicines = []
    selected_store = None
    customer = request.user
    medicine_requests = MedicineRequest.objects.filter(customer=customer)

    if store_id:
        selected_store = get_object_or_404(MediRegistration, id=store_id)
        medicines = Medicine.objects.filter(medical_store=store_id)

    if request.method == 'POST' and 'upload_request' in request.POST:
        name = request.POST.get('name') or "Unnamed"
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if image:
            MedicineRequest.objects.create(
                customer=customer,
                name=name,
                image=image,
                description=description
            )
            messages.success(request, "Your request has been uploaded successfully!")
            return redirect('browse-non-prescription', store_id=store_id)
        else:
            messages.error(request, "Please upload an image.")

    context = {
        'stores': stores,
        'selected_store': selected_store,
        'selected_store_id': store_id,
        'medicines': medicines,
        'medicine_requests': medicine_requests,
    }
    return render(request, 'customer/non_prescription.html', context)




@login_required
def non_prescription(request, store_id=None):
    stores = MediRegistration.objects.all()  # Updated to MediRegistration
    medicines = []
    selected_store = None
    medicine_requests = MedicineRequest.objects.filter(
        customer=request.user)  # Get requests made by the logged-in customer

    if store_id:
        selected_store = get_object_or_404(MediRegistration, id=store_id)  # Updated to MediRegistration
        medicines = Medicine.objects.filter(store=selected_store)  # Medicines linked to the selected store

    # Handle customer medicine request upload
    if request.method == 'POST' and 'upload_request' in request.POST:
        image = request.FILES.get('image')
        name = request.POST.get('name') or "Unnamed"
        description = request.POST.get('description')

        # Save the medicine request by the customer
        if image:
            MedicineRequest.objects.create(customer=request.user, name=name, image=image, description=description)

            # Redirect with success message
            messages.success(request, 'Your medicine request has been successfully uploaded!')

        return redirect('browse-non-prescription', store_id=store_id)

    context = {
        'stores': stores,
        'medicines': medicines,
        'selected_store': selected_store,
        'selected_store_id': store_id,
        'medicine_requests': medicine_requests,
    }

    return render(request, 'customer/non_prescription.html', context)


# ------------------------
# Add to Cart View
# ------------------------
@login_required
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)  # Get the medicine by ID
    customer = request.user
    quantity = int(request.POST.get('quantity', 1))  # Default quantity is 1 if not provided

    # Check if the item already exists in the cart for the customer
    cart_item, created = CartItem.objects.get_or_create(customer=customer, medicine=medicine)

    if not created:
        cart_item.quantity += quantity  # If item already in cart, just update the quantity
    else:
        cart_item.quantity = quantity  # Set the quantity if it's a new item

    cart_item.save()  # Save the cart item

    # Redirect to the selected store's page using the correct store reference
    return redirect('browse-non-prescription', store_id=medicine.medical_store.id)  # Updated





@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'Customer/cart.html', {'cart_items': cart_items, 'total': total})


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CartItem


@login_required
@require_POST
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, customer=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    item.save()
    return redirect('cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, customer=request.user)
    item.delete()
    return redirect('cart')


from .models import CartItem, Medicine

from .forms import ShippingDetailsForm

from django.contrib.auth.decorators import login_required


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(customer=request.user)

    if not cart_items.exists():
        return render(request, 'Customer/empty_cart.html')

    # Calculate totals
    total_price = sum(item.total_price() for item in cart_items)
    gst_rate = Decimal('0.18')
    gst = total_price * gst_rate
    grand_total = total_price + gst

    # Get the medical store from first cart item
    medical_store = cart_items.first().medicine.medical_store

    if request.method == 'POST':
        form = ShippingDetailsForm(request.POST)
        if form.is_valid():
            shipping_details = form.save(commit=False)
            shipping_details.customer = request.user
            shipping_details.medical_store = medical_store
            shipping_details.save()
            return redirect('order_confirmation')
    else:
        form = ShippingDetailsForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst': gst,
        'grand_total': grand_total,
        'form': form,
        'medical_store': medical_store,  # ✅ Pass the full store object
    }

    return render(request, 'Customer/checkout.html', context)





# @login_required
# def cart_view(request):
#     cart_items = CartItem.objects.filter(customer=request.user)
#     total = sum(item.total_price() for item in cart_items)
#     return render(request, 'Customer/cart.html', {'cart_items': cart_items, 'total': total})
#
#
# @login_required
# @require_POST
# def update_cart_quantity(request, item_id):
#     item = get_object_or_404(CartItem, id=item_id, customer=request.user)
#     action = request.POST.get('action')
#
#     if action == 'increase':
#         item.quantity += 1
#     elif action == 'decrease' and item.quantity > 1:
#         item.quantity -= 1
#     item.save()
#     return redirect('cart')
#
#
# @login_required
# @require_POST
# def remove_from_cart(request, item_id):
#     item = get_object_or_404(CartItem, id=item_id, customer=request.user)
#     item.delete()
#     return redirect('cart')
#
# from decimal import Decimal
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .models import CartItem
# from .forms import ShippingDetailsForm
#
# @login_required
# def checkout(request):
#     cart_items = CartItem.objects.filter(customer=request.user)
#
#     if not cart_items.exists():
#         return render(request, 'Customer/cart.html')
#
#     total_price = sum(item.total_price() for item in cart_items)
#     gst_rate = Decimal('0.18')
#     gst = total_price * gst_rate
#     grand_total = total_price + gst
#
#     medical_store = cart_items.first().medicine.medical_store
#     medical_store_address = medical_store.address
#
#     success = False  # ✅ Track confirmation status
#
#     if request.method == 'POST':
#         form = ShippingDetailsForm(request.POST)
#
#         if form.is_valid():
#             shipping_details = form.save(commit=False)
#             shipping_details.customer = request.user
#             shipping_details.medical_store = medical_store
#             shipping_details.save()
#
#             # 🧹 Optional: Clear cart
#             cart_items.delete()
#
#             success = True  # ✅ Set flag to show tick
#
#     else:
#         form = ShippingDetailsForm()
#
#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'gst': gst,
#         'grand_total': grand_total,
#         'form': form,
#         'medical_store': medical_store,
#         'medical_store_address': medical_store_address,
#         'success': success  # ✅ Pass to templates
#     }
#
#     return render(request, 'Customer/checkout.html', context)

@login_required
def order_confirmation(request):
    cart_items = CartItem.objects.filter(customer=request.user)

    if not cart_items.exists():
        return render(request, 'Customer/cart.html')

    total_price = sum(item.total_price() for item in cart_items)
    gst_rate = Decimal('0.18')
    gst = total_price * gst_rate
    grand_total = total_price + gst

    # Get the medical store from the first cart item
    medical_store = cart_items.first().medicine.medical_store
    medical_store_address = medical_store.address

    # Fetch the shipping details
    shipping_details = request.user.shippingdetails.all().first()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst': gst,
        'grand_total': grand_total,
        'medical_store': medical_store,
        'medical_store_address': medical_store_address,
        'shipping_details': shipping_details
    }

    return render(request, 'Customer/order_confirmation.html', context)


@login_required
def download_invoice_pdf(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    gst_rate = Decimal('0.18')
    gst = total_price * gst_rate
    grand_total = total_price + gst

    # Get the medical store from the first cart item
    medical_store = cart_items.first().medicine.medical_store
    medical_store_address = medical_store.address

    # Fetch shipping details
    shipping_details = request.user.shippingdetails.all().first()

    template_path = 'Customer/checkout_pdf.html'
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'gst': gst,
        'grand_total': grand_total,
        'request': request,
        'medical_store': medical_store,
        'medical_store_address': medical_store_address,
        'shipping_details': shipping_details
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response

# ======================================================================================================
def generate_pdf(order):
    # Create a PDF buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Add content to the PDF
    c.drawString(100, 750, f"Order Confirmation for {order.customer.name}")
    c.drawString(100, 730, f"Order ID: {order.id}")
    c.drawString(100, 710, f"Total Price: ${order.total_price}")
    c.drawString(100, 690, f"Items: {', '.join([item.medicine.name for item in order.items.all()])}")

    # Add Medical Store Info
    c.drawString(100, 670, f"Medical Store: {order.medical_store.store_name}")
    c.drawString(100, 650, f"Store Address: {order.medical_store.address}")

    # Add Shipping Address Info
    if order.shippingdetails:
        c.drawString(100, 630, f"Shipping Address: {order.shippingdetails.address}")

    # Save the PDF to the buffer
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


from django.core.mail import EmailMessage
from django.conf import settings


def send_order_email_with_pdf(order):
    # Generate the PDF
    pdf_buffer = generate_pdf(order)

    # Prepare the email
    subject = f"Order Confirmation: {order.id}"
    body = f"Dear {order.customer.name},\n\nYour order has been confirmed. Please find the attached PDF for your order details."
    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [order.customer.email])

    # Attach the PDF
    email.attach(f"Order_{order.id}.pdf", pdf_buffer.read(), 'application/pdf')

    # Send the email
    email.send()


def confirm_payment_and_send_email(order):
    # Here you can add the logic to confirm the payment
    order.payment_status = 'confirmed'  # Example status update
    order.save()

    # Now send the email with PDF
    send_order_email_with_pdf(order)


import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order, Payment
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas


# Create Razorpay Order (Frontend trigger)
def create_payment_order(request, order_id):
    order = Order.objects.get(id=order_id)
    total_amount = order.grand_total

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_data = client.order.create({
        'amount': total_amount * 100,  # Amount in paise
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Save order data to the database
    payment = Payment.objects.create(
        order=order,
        razorpay_order_id=order_data['id']
    )

    return JsonResponse({
        'order_id': order_data['id'],
        'key_id': settings.RAZORPAY_KEY_ID
    })


# Handle Razorpay payment confirmation (Backend)
def verify_payment(request):
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        })

        # Mark payment as successful
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.payment_status = 'successful'
        payment.save()

        # Update order status
        order = payment.order
        order.status = 'completed'
        order.save()

        # Send email with PDF invoice
        send_invoice_email(order)

        return JsonResponse({'status': 'success', 'message': 'Payment successful'})
    except Exception as e:
        # Handle payment verification failure
        return JsonResponse({'status': 'failure', 'message': str(e)})


# Generate and send invoice PDF via email
def send_invoice_email(order):
    # Generate the PDF
    pdf = generate_invoice_pdf(order)

    # Prepare the email
    subject = "Your Invoice from RxRapid"
    message = "Thank you for your purchase. Please find the attached invoice for your order."
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.customer.email]

    send_mail(subject, message, email_from, recipient_list, fail_silently=False,
              html_message=render_to_string('invoice_email.html', {'order': order}),
              attachments=[('invoice.pdf', pdf, 'application/pdf')])


# Generate the PDF for the invoice
def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Add content to the PDF (Invoice details)
    p.drawString(100, 750, f"Invoice for Order {order.id}")
    p.drawString(100, 730, f"Customer: {order.customer.name}")
    p.drawString(100, 710, f"Store: {order.medical_store.name}")
    p.drawString(100, 690, f"Total: ₹{order.grand_total}")

    # More content, such as medicines, etc.
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.read()


from django.shortcuts import redirect, get_object_or_404

import uuid
from django.core.mail import send_mail
from .models import Payment, CartItem, Order, CustomerUser
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
@csrf_exempt
def process_payment(request):
    user = request.user

    try:
        customer = CustomerUser.objects.get(email=user.email)
    except CustomerUser.DoesNotExist:
        return render(request, 'error.html', {'message': 'Customer not found.'})

    cart_items = CartItem.objects.filter(customer=customer)

    if not cart_items.exists():
        return render(request, 'error.html', {'message': 'Your cart is empty.'})

    # Calculate total price
    total_price = Decimal('0.00')
    for item in cart_items:
        item_total = Decimal(item.medicine.price) * item.quantity
        total_price += item_total

    gst = (total_price * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = (total_price + gst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Ensure a medical store is assigned to the order
        first_item = cart_items.first()
        store = first_item.medicine.medical_store if first_item else None

        if not store:
            return render(request, 'error.html', {'message': 'Unable to identify store.'})

        # Create the order
        order = Order.objects.create(
            customer=customer,
            medical_store=store,  # Assign medical store to the order
            total_price=total_price,
            gst=gst,
            grand_total=grand_total,
            payment_method=payment_method,
            status='pending',  # Set as 'pending' initially
        )

        # Handle Cash on Delivery (COD) payment method
        if payment_method == 'cod':
            cart_items.delete()

            # Create payment record for COD
            payment = Payment.objects.create(
                order=order,
                payment_id=f"RXR-{uuid.uuid4().hex[:10].upper()}",
                payment_status='success',  # Payment is successful for COD
            )

            # Send email receipt for COD
            send_mail(
                subject="RxRapid Payment Receipt",
                message=f"""
Hi {customer.name}, 

Your Order request is sent successfully !

🧾 Receipt Number: {payment.payment_id}
📦 Order ID: {order.id}
💰 Total: ₹{grand_total}
📅 Date: {payment.created_at.strftime('%d %b %Y, %I:%M %p')}

Thank you for using RxRapid!
                """,
                from_email="internhimanshu3@gmail.com",  # Your email here
                recipient_list=[customer.email],
                fail_silently=False,
            )

            # Render the payment success page for COD
            return render(request, 'Customer/payment_success.html', {
                'payment_method': 'Cash on Delivery',
                'total_price': total_price,
                'gst': gst,
                'grand_total': grand_total,
                'payment': payment,
                'order': order,
            })

        # Handle online payment method
        elif payment_method == 'online':
            # For online payment, redirect to the online payment placeholder page
            return render(request, 'Customer/online_payment_placeholder.html', {
                'store': store,  # Pass the store info to the page
                'order': order,  # Pass the order details to the page
                'total_price': total_price,
                'gst': gst,
                'grand_total': grand_total,
            })

        else:
            return render(request, 'error.html', {'message': 'Invalid payment method selected.'})

    # If not POST, redirect to checkout page
    return redirect('checkout')


# If someone accesses without POST
@login_required
def upload_prescription_confirm(request):
    return render(request, 'customer/upload_success.html')



from django.shortcuts import render, redirect
from django.urls import reverse


# Your view to handle the payment processing
def payment_gateway_integration(request, store_id):
    # Logic to interact with the payment gateway (e.g., Razorpay, Stripe)

    store = get_object_or_404(MediRegistration, id=store_id)  # Assuming you have a store model

    # Your logic for payment integration here
    # For example, creating an order, redirecting to a payment gateway, etc.

    return render(request, 'payment_gateway_integration.html', {'store': store})


from decimal import Decimal, ROUND_HALF_UP
from .models import CartItem, MediRegistration, CustomerUser


@login_required
def upload_prescription_confirm(request):
    return render(request, 'customer/upload_success.html')


from django.shortcuts import render, redirect
from django.urls import reverse


# Your view to handle the payment processing
def payment_gateway_integration(request, store_id):
    # Logic to interact with the payment gateway (e.g., Razorpay, Stripe)

    store = get_object_or_404(MediRegistration, id=store_id)  # Assuming you have a store model

    # Your logic for payment integration here
    # For example, creating an order, redirecting to a payment gateway, etc.

    return render(request, 'payment_gateway_integration.html', {'store': store})


from decimal import Decimal, ROUND_HALF_UP
from .models import CartItem, MediRegistration, CustomerUser




@require_POST
@login_required
def process_online_method(request):
    user = request.user
    online_method = request.POST.get('online_method')
    store_id = request.POST.get('store_id')

    # Validate the selected method
    if online_method not in ['upi', 'card', 'netbanking', 'manual']:
        return render(request, 'error.html', {'message': 'Invalid online payment method selected.'})

    # Validate store
    try:
        store = MediRegistration.objects.get(id=store_id)
    except MediRegistration.DoesNotExist:
        return render(request, 'error.html', {'message': 'Medical store not found.'})

    # Get customer
    try:
        customer = CustomerUser.objects.get(email=user.email)
    except CustomerUser.DoesNotExist:
        return render(request, 'error.html', {'message': 'Customer not found.'})

    # Fetch cart items
    cart_items = CartItem.objects.filter(customer=customer)
    if not cart_items.exists():
        return render(request, 'error.html', {'message': 'Your cart is empty. Please add items before paying.'})

    # Calculate totals
    total_price = Decimal('0.00')
    for item in cart_items:
        item_total = Decimal(item.medicine.price) * item.quantity
        total_price += item_total

    gst = (total_price * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = (total_price + gst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Optionally: Clear the cart after payment (simulate payment success)
    cart_items.delete()

    # Render success page
    return render(request, 'Customer/payment_success.html', {
        'payment_method': online_method.upper(),
        'store': store,
        'total_price': total_price,
        'gst': gst,
        'grand_total': grand_total
    })


from django.shortcuts import render, redirect
from django.contrib import messages


def contact_us(request):
    if request.method == "POST":
        # You can add email or DB logic here
        messages.success(request, "Thank you for contacting us. We will get back to you shortly.")
        return redirect('contact-us')
    return render(request, 'Customer/contact_us.html')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Prescription
from medical.models import PrescriptionBill  # adjust your import if needed

# imports
import razorpay
from django.conf import settings

@login_required
def view_invoice(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, customer=request.user)
    bill = PrescriptionBill.objects.filter(prescription=prescription, customer=request.user).first()

    if not bill:
        return HttpResponse("No bill available for this prescription.", status=404)

    customer = bill.customer
    items = bill.items.all()

    # Calculate total


    subtotal = sum(Decimal(item.quantity) * item.mrp for item in items)
    gst = subtotal * Decimal('0.18')
    grand_total = subtotal + gst

    # Create Razorpay Order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment_order = client.order.create({
        "amount": int(grand_total * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": 1
    })

    order_id = payment_order['id']

    context = {
        'bill': bill,
        'customer': customer,
        'prescription': prescription,
        'items': items,
        'grand_total': grand_total,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order_id,
    }
    return render(request, 'customer/view_invoice.html', context)

@require_POST
@login_required
def confirm_delivery(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, customer=request.user)
    prescription.status = 'delivered'
    prescription.save()
    messages.success(request, "Your delivery has been confirmed. Thank you!")
    return redirect('view_invoice', prescription_id=prescription.id)


# Customer/views.py
from django.shortcuts import render, redirect
from .forms import CustomerIssueForm
from .models import CustomerIssue

def create_issue(request):
    if request.method == 'POST':
        form = CustomerIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.customer = request.user
            issue.save()
            return redirect('customer-issue-submitted')  # Redirect after submit
    else:
        form = CustomerIssueForm()
    return render(request, 'customer/create_issue.html', {'form': form})

def issue_submitted(request):
    return render(request, 'customer/issue_submitted.html')


from django.shortcuts import render

def about_view(request):
    template = loader.get_template('Customer/about.html')
    return HttpResponse(template.render())