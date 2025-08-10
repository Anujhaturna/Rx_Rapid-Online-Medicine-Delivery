from django.shortcuts import render, redirect, get_object_or_404
from .form import LoginForm
from .form import MedRegistrationForm
from .models import MediRegistration
from .form import MedicineForm
from datetime import date
from .models import PrescriptionBill, PrescriptionBillItem
from django.forms import modelformset_factory
from django.core.mail import send_mail
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from decimal import Decimal
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
import os
from django.db.models import Subquery, OuterRef
from django.conf import settings
from .form import PrescriptionBillItemForm
from django.shortcuts import render, get_object_or_404
from Customer.models import CustomerUser, MedicineRequest, Prescription
from Customer.models import Order
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MediRegistration, Medicine
from .form import MedicineForm


def medical_registration(request):
    if request.method == 'POST':
        form = MedRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_approved = False
            instance.save()
            messages.success(request, "Registration submitted successfully! Wait for admin approval.")
            return redirect('medical:medical_registration')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MedRegistrationForm()

    return render(request, 'medical/medical_registration.html', {'form': form})


def medical_login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                user = MediRegistration.objects.get(username=username)

                if user.password == password:
                    if user.is_approved:
                        request.session['user_id'] = user.id
                        messages.success(request, "Login successful!")
                        return redirect('medical:medical_dashboard')
                    else:
                        messages.warning(request, "Your registration is not yet approved by the admin.")
                else:
                    messages.error(request, "Invalid password.")
            except MediRegistration.DoesNotExist:
                messages.error(request, "Invalid username.")

    return render(request, 'medical/medical_login.html', {'form': form})


# You should have a ModelForm for Medicine

def medical_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to access the dashboard.")
        return redirect('medical:medical_login')

    try:
        user = MediRegistration.objects.get(id=user_id)
    except MediRegistration.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('medical:medical_login')

    medicines = user.medicines.all()

    return render(request, 'medical/medical_dashboard.html', {
        'user': user,
        'medicines': medicines
    })


def edit_medicine(request, medicine_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to continue.")
        return redirect('medical:medical_login')

    user = get_object_or_404(MediRegistration, id=user_id)
    medicine = get_object_or_404(Medicine, id=medicine_id, medical_store=user)

    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated successfully.")
            return redirect('medical:medical_dashboard')
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'medical/edit_medicine.html', {'form': form})


def delete_medicine(request, medicine_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to continue.")
        return redirect('medical:medical_login')

    user = get_object_or_404(MediRegistration, id=user_id)
    medicine = get_object_or_404(Medicine, id=medicine_id, medical_store=user)

    if request.method == 'POST':
        medicine.delete()
        messages.success(request, "Medicine deleted successfully.")

    return redirect('medical:medical_dashboard')


# Function: logout
def medical_logout(request):
    request.session.flush()  # Clears the entire session
    messages.success(request, "Logged out successfully.")
    return redirect('medical_login')


def add_medicine(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to add medicine.")
        return redirect('medical:medical_login')

    try:
        medical_store = MediRegistration.objects.get(id=user_id)
        if not medical_store.is_approved:
            messages.warning(request, "Your registration is not yet approved.")
            return redirect('medical_dashboard')
    except MediRegistration.DoesNotExist:
        messages.error(request, "Medical store not found.")
        return redirect('login')

    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)  # ✅ Include request.FILES
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.medical_store = medical_store
            medicine.save()
            messages.success(request, "Medicine added successfully!")
            return redirect('medical:medical_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MedicineForm()

    return render(request, 'medical/add_medicine.html', {'form': form})


def view_uploaded_prescriptions(request):
    # Check if the user is logged in

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to access your prescriptions.")
        return redirect('medical:medical_login')

    # Fetch the MediRegistration user
    try:
        user = MediRegistration.objects.get(id=user_id)
    except MediRegistration.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('medical:medical_login')

    today = date.today()

    # Optional: filter prescriptions for a specific patient if needed
    patient_id = request.GET.get('patient_id')
    if patient_id:
        try:
            customer = CustomerUser.objects.get(id=patient_id)
            prescriptions = Prescription.objects.filter(
                customer=customer,
                upload_time__date=today  # ✅ Corrected field name
            )
        except CustomerUser.DoesNotExist:
            messages.error(request, "Patient not found.")
            return redirect('medical:medical_dashboard')
    else:
        # Load all prescriptions for today if no patient specified
        prescriptions = Prescription.objects.filter(upload_time__date=today)  # ✅ Corrected

        customer = None

    # Annotate prescriptions with their bill (if exists)
    prescriptions = prescriptions.annotate(
        bill_id=Subquery(
            PrescriptionBill.objects.filter(prescription=OuterRef('pk')).values('id')[:1]
        )
    )
    medreq = MedicineRequest.objects.all()
    return render(request, 'medical/view_uploaded_prescriptions.html', {
        'user': user,
        'prescriptions': prescriptions,
        'customer': customer,
        'medicine_requests': medreq
    })


# from django.shortcuts import render, get_object_or_404
# from Customer.models import Prescription, MedicineRequest, CustomerUser
#
#
# def customer_documents_view(request, customer_id):
#     customer = get_object_or_404(CustomerUser, id=customer_id)
#
#     prescriptions = Prescription.objects.filter(customer=customer)
#     medicine_requests = MedicineRequest.objects.filter(customer=customer)
#
#     return render(request, 'medical/customer_documents.html', {
#         'customer': customer,
#         'prescriptions': prescriptions,
#         'medicine_requests': medicine_requests,
#     })

def view_prescription_and_generate_bill(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    customer = prescription.customer

    # ✅ Get user_id from session instead of request.user
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login to access your prescriptions.")
        return redirect('medical_login')

    medical_store = get_object_or_404(MediRegistration, id=user_id)

    PrescriptionBillItemFormSet = modelformset_factory(
        PrescriptionBillItem, form=PrescriptionBillItemForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        formset = PrescriptionBillItemFormSet(request.POST)
        if formset.is_valid():
            bill = PrescriptionBill.objects.create(
                prescription=prescription,
                customer=customer,
                medical_store=medical_store,
            )

            total_amount = 0
            items = []
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    item = form.save(commit=False)
                    item.bill = bill
                    item.amount = item.mrp * item.quantity
                    item.save()
                    items.append(item)
                    total_amount += item.amount

            bill.total_amount = total_amount
            bill.save()

            # ✅ Generate PDF
            bill_folder = os.path.join(settings.MEDIA_ROOT, 'bills')
            os.makedirs(bill_folder, exist_ok=True)
            pdf_path = os.path.join(bill_folder, f"bill_{bill.id}.pdf")
            generate_pdf(bill, items, pdf_path)

            # ✅ Build URL for preview
            pdf_url = os.path.join(settings.MEDIA_URL, 'bills', f"bill_{bill.id}.pdf")

            messages.success(request, 'Bill generated successfully!')

            return render(request, 'medical/generate_bill.html', {
                'prescription': prescription,
                'formset': PrescriptionBillItemFormSet(queryset=PrescriptionBillItem.objects.none()),
                'customer': customer,
                'bill_generated': True,
                'pdf_url': pdf_url,
                'bill': bill
            })
    else:
        formset = PrescriptionBillItemFormSet(queryset=PrescriptionBillItem.objects.none())

    return render(request, 'medical/generate_bill.html', {
        'prescription': prescription,
        'formset': formset,
        'customer': customer
    })


def generate_pdf(bill, items, filepath):
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles['Heading2']
    title_style = ParagraphStyle(
        name='CenterTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.darkblue,
        alignment=1,  # center
        spaceAfter=20
    )

    doc = SimpleDocTemplate(filepath, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=60)
    elements = []

    # Header
    elements.append(Paragraph("RxRapid Invoice", title_style))

    # Customer Info
    elements.append(Paragraph("<b>Customer Info</b>", heading))
    elements.append(Paragraph(f"Name: {bill.customer.name}", normal))
    elements.append(Paragraph(f"Phone: {bill.customer.phone}", normal))
    elements.append(Paragraph(f"Email: {bill.customer.email}", normal))
    elements.append(Paragraph(f"Address: {bill.customer.address}", normal))
    elements.append(Spacer(1, 12))

    # Store Info
    elements.append(Paragraph("<b>Medical Store</b>", heading))
    elements.append(Paragraph(f"Store: {bill.medical_store.store_name}", normal))
    elements.append(Paragraph(f"Shop No: {bill.medical_store.shop_no}", normal))
    elements.append(Paragraph(f"Contact: {bill.medical_store.contact}", normal))
    elements.append(Paragraph(f"Email: {bill.medical_store.email}", normal))
    elements.append(Paragraph(f"Address: {bill.medical_store.address}", normal))
    elements.append(Paragraph(f"{bill.medical_store.city}, {bill.medical_store.state}", normal))
    elements.append(Paragraph(f"Pincode: {bill.medical_store.pincode}", normal))
    elements.append(Spacer(1, 12))

    # Table Header
    table_data = [['Medicine', 'Expiry', 'Qty', 'Price', 'Total']]
    subtotal = Decimal(0)
    for item in items:
        total = Decimal(item.quantity) * Decimal(item.mrp)
        table_data.append([
            item.medicine_name,
            item.expiry_date.strftime('%b %Y'),
            str(item.quantity),
            f"₹{Decimal(item.mrp):.2f}",
            f"₹{total:.2f}"
        ])
        subtotal += total

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    elements.append(Table(table_data, style=table_style))
    elements.append(Spacer(1, 12))

    # Totals
    gst = subtotal * Decimal('0.18')
    grand_total = subtotal + gst

    totals_data = [
        ['', '', '', 'Subtotal:', f"₹{subtotal:.2f}"],
        ['', '', '', 'GST (18%):', f"₹{gst:.2f}"],
        ['', '', '', 'Grand Total:', f"₹{grand_total:.2f}"]
    ]
    totals_style = TableStyle([
        ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
        ('FONTNAME', (3, 0), (4, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (3, 2), (4, 2), colors.darkblue),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ])
    elements.append(Table(totals_data, style=totals_style))
    elements.append(Spacer(1, 24))

    # Footer
    elements.append(Paragraph(
        "<para align=center><font size=14 color=green>Thank you for choosing RxRapid!</font></para>", normal
    ))
    elements.append(Paragraph(
        "<para align=center><font size=8>(System-generated invoice)</font></para>", normal
    ))

    # Watermark Canvas Function
    def add_watermark(canvas_obj, doc_obj):
        watermark_path = finders.find('images/rxrapid_watermark.jpg')
        if watermark_path and os.path.exists(watermark_path):
            canvas_obj.saveState()
            canvas_obj.setFillAlpha(0.08)  # Light transparency
            x = A4[0] / 2 - 150
            y = A4[1] / 2 - 150
            canvas_obj.drawImage(watermark_path, x, y, width=300, height=300, preserveAspectRatio=True, mask='auto')
            canvas_obj.restoreState()

    # Add PageTemplate with watermark
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='with-watermark', frames=frame, onPage=add_watermark)
    doc.addPageTemplates([template])

    # Build the document
    doc.build(elements)


def notify_patient(request, bill_id):
    bill = get_object_or_404(PrescriptionBill, id=bill_id)
    items = PrescriptionBillItem.objects.filter(bill=bill)

    # Calculate totals
    subtotal = sum(item.quantity * item.mrp for item in items)
    gst = subtotal * Decimal('0.18')
    grand_total = subtotal + gst

    # Email content
    subject = f"RxRapid Invoice Summary - Bill #{bill.id}"
    recipient = bill.customer.email
    from_email = settings.DEFAULT_FROM_EMAIL

    html_message = render_to_string('medical/simple_bill_email.html', {
        'customer': bill.customer,
        'store': bill.medical_store,
        'items': items,
        'subtotal': f"₹{subtotal:.2f}",
        'gst': f"₹{gst:.2f}",
        'grand_total': f"₹{grand_total:.2f}",
        'bill_id': bill.id
    })

    try:
        send_mail(
            subject,
            '',  # plain message fallback
            from_email,
            [recipient],
            html_message=html_message
        )
        bill.is_notified = True
        bill.save()
        messages.success(request, "Patient has been notified via email.")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")

    return redirect('medical:medical_dashboard')


# from django.shortcuts import render, get_object_or_404, redirect
# from Customer.models import Order  # Adjust if your model is named differently
# from django.views.decorators.http import require_POST
#
# def confirm_order_view(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     return render(request, 'medical/confirm_order.html', {'order': order})
#
# @require_POST
# def approve_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     order.status = 'approved'
#     order.save()
#     return redirect('medical:confirm_order', order_id=order.id)


def customer_prescriptions_view(request, customer_id):
    customer = get_object_or_404(CustomerUser, id=customer_id)

    prescriptions = Prescription.objects.filter(customer=customer)
    medicine_requests = MedicineRequest.objects.filter(customer=customer)  # ✅ This line is important!

    return render(request, 'view_uploaded_prescriptions.html', {
        'customer': customer,
        'prescriptions': prescriptions,
        'medicine_requests': medicine_requests,  # ✅ Pass this to the template
    })


# views.py 
from django.shortcuts import render, redirect
from Customer.models import Order
from medical.models import MediRegistration


from django.shortcuts import render, redirect
from Customer.models import Order
from medical.models import MediRegistration

def view_non_prescription_orders(request):
    if 'user_id' not in request.session:
        return redirect('medical_login')

    try:
        medical_user = MediRegistration.objects.get(id=request.session['user_id'])
    except MediRegistration.DoesNotExist:
        return redirect('medical_login')

    # Use select_related to prefetch related foreign keys (medicine + customer)
    orders = Order.objects.filter(medical_store=medical_user, status='pending').select_related('medicine', 'customer')

    return render(request, 'medical/non_prescription_orders.html', {'orders': orders})


def confirm_order(request, order_id):
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        medical_user = MediRegistration.objects.get(id=request.session['user_id'])
    except MediRegistration.DoesNotExist:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, medical_store=medical_user)
    order.status = 'delivered'
    order.save()
    messages.success(request, f"Order #{order.id} marked as delivered.")
    return redirect('medical:view_non_prescription_orders')


from django.shortcuts import render, redirect
from Manager.models import Notification
from medical.models import MediRegistration
from django.db.models import Q
from django.contrib import messages

from django.shortcuts import render, redirect
from Manager.models import Notification
from medical.models import MediRegistration
from django.db.models import Q
from django.contrib import messages

from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from .models import MediRegistration
from Manager.models import Notification
from django.shortcuts import render
from Manager.models import Notification


def medical_store_notifications(request):
    notifications = Notification.objects.filter(
        send_to='all'  # 🔥 Only fetch notifications sent to 'all'
    ).order_by('-created_at')

    context = {
        'notifications': notifications,
    }
    return render(request, 'medical/notifications.html', context)
