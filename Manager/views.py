from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages

from medical.models import MediRegistration, MedicalIssue
from Customer.models import Prescription  # Correctly import from the user app

from Customer.models import Order, CustomerIssue

MANAGER_USERNAME = 'a@gmail.com'
MANAGER_PASSWORD = '1234'


from django.shortcuts import render
from medical.models import MediRegistration
from Customer.models import Order
from Customer.models import Prescription
from Customer.models import CustomerIssue
from medical.models import MedicalIssue

def manager_dashboard(request):
    # Count data for dashboard
    total_stores = MediRegistration.objects.count()
    pending_approvals = MediRegistration.objects.filter(is_approved=False).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    unresolved_customer_issues = CustomerIssue.objects.filter(is_read='True').count()
    unresolved_medical_issues = MedicalIssue.objects.filter(status='Open').count()

    # Fetch lists of bills and orders
    bills = Prescription.objects.select_related('customer', 'medical_store').all()
    orders = Order.objects.select_related('customer', 'medical_store').all()

    context = {
        'total_stores': total_stores,
        'pending_approvals': pending_approvals,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'unresolved_customer_issues': unresolved_customer_issues,
        'unresolved_medical_issues': unresolved_medical_issues,
        'bills': bills,
        'orders': orders,
    }
    return render(request, 'manager/dashboard.html', context)


def manage_stores(request):
    stores = MediRegistration.objects.all()
    return render(request, 'manager/manage_stores.html', {'stores': stores})


def view_store(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    return render(request, 'manager/view_store.html', {'store': store})


def remove_store(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    store.delete()
    return redirect('manage_stores')


def store_prescriptions(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    prescriptions = Prescription.objects.filter(store=store)
    return render(request, 'manager/store_prescriptions.html', {
        'store': store,
        'prescriptions': prescriptions,
    })





from django.shortcuts import render
from medical.models import PrescriptionBill  # import the model

from django.shortcuts import render
from django.shortcuts import render
from medical.models import PrescriptionBill
from medical.models import MediRegistration
from django.db.models import Q
from Customer.models import Order
from django.db.models import Sum





# Your view function
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from collections import defaultdict
from django.shortcuts import render
import json
from Customer.models import Order
from medical.models import PrescriptionBill, MediRegistration
from decimal import Decimal


def sales_report(request):
    orders = Order.objects.all()
    bills = PrescriptionBill.objects.all()
    medical_stores = MediRegistration.objects.all()

    selected_store_id = request.GET.get('medical_store')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if selected_store_id:
        orders = orders.filter(medical_store_id=selected_store_id)
        bills = bills.filter(medical_store_id=selected_store_id)

    if from_date and to_date:
        orders = orders.filter(created_at__date__range=[from_date, to_date])
        bills = bills.filter(generated_at__date__range=[from_date, to_date])

    # Total income
    order_income = orders.aggregate(total=Sum('total_price'))['total'] or Decimal("0.0")
    prescription_income = bills.aggregate(total=Sum('total_amount'))['total'] or Decimal("0.0")
    total_income = order_income + prescription_income

    # Month-wise aggregation
    order_months = orders.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_price'))
    bill_months = bills.annotate(month=TruncMonth('generated_at')).values('month').annotate(total=Sum('total_amount'))

    # ✅ Merge both sources into one dict by month (Decimal-safe)
    from collections import defaultdict
    monthwise_data = defaultdict(lambda: Decimal("0.0"))

    for entry in order_months:
        if entry['month']:
            month_key = entry['month'].strftime('%B %Y')
            monthwise_data[month_key] += entry['total'] or Decimal("0.0")

    for entry in bill_months:
        if entry['month']:
            month_key = entry['month'].strftime('%B %Y')
            monthwise_data[month_key] += entry['total'] or Decimal("0.0")

    # ✅ Prepare data for Chart.js
    pie_labels = list(monthwise_data.keys())
    pie_values = [float(value) for value in monthwise_data.values()]  # Convert Decimal to float for JSON

    context = {
        'orders': orders,
        'bills': bills,
        'medical_stores': medical_stores,
        'selected_store_id': selected_store_id,
        'from_date': from_date,
        'to_date': to_date,
        'total_income': total_income,
        'pie_labels': json.dumps(pie_labels),
        'pie_values': json.dumps(pie_values),
    }
    return render(request, 'manager/sales_report.html', context)

def manager_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'manager/manager_login.html')


from django.shortcuts import render, get_object_or_404
from medical.models import MediRegistration
from Customer.models import Prescription


def view_prescriptions(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    prescriptions = Prescription.objects.filter(store=store)
    return render(request, 'manager/prescription_list.html', {
        'store': store,
        'prescriptions': prescriptions
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ManagerProfile
from .forms import ManagerProfileForm


@login_required
def manager_profile(request):
    # Get the manager profile or create a new one
    manager_profile, created = ManagerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, request.FILES, instance=manager_profile)
        if form.is_valid():
            form.save()
            return redirect('manager_profile')  # Redirect after saving the profile
    else:
        form = ManagerProfileForm(instance=manager_profile)

    return render(request, 'manager/manager_profile.html', {'form': form})


from django.shortcuts import redirect, get_object_or_404
from .models import MediRegistration


def approve_store(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    store.is_approved = True
    store.save()
    return redirect('manage_stores')  # Make sure this is your actual URL name for manage stores


def reject_store(request, store_id):
    store = get_object_or_404(MediRegistration, id=store_id)
    store.is_approved = False
    store.save()
    return redirect('manage_stores')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MediRegistration, Notification
from .form1 import NotificationForm

def sent_notifications(request):
    notifications = Notification.objects.all().order_by('-scheduled_date')
    return render(request, 'manager/notifications_view.html', {'notifications': notifications})
def send_notifications(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)

        if form.is_valid():
            message = form.cleaned_data['message']
            scheduled_date = form.cleaned_data['scheduled_date']

            approved_stores = MediRegistration.objects.filter(is_approved=True)

            if approved_stores.exists():
                for store in approved_stores:
                    Notification.objects.create(
                        medical_store=store,
                        message=message,
                        scheduled_date=scheduled_date,
                    )
                messages.success(request, "✅ Notification sent to all approved medical stores!")
            else:
                messages.error(request, "⚠️ No approved medical stores found.")

            return redirect('send_notifications')  # or 'sent_notifications' if you have a sent list page

        else:
            messages.error(request, "❌ Form is invalid. Please correct the errors.")

    else:
        form = NotificationForm()

    return render(request, 'manager/send_notifications.html', {'form': form})
from django.shortcuts import render, redirect
from Customer.forms import CustomerIssueForm
from django.contrib.auth.decorators import login_required

@login_required
def create_issues(request):
    if request.method == 'POST':
        form = CustomerIssueForm(request.POST)
        if form.is_valid():
            # Assign the issue to the logged-in customer
            issue = form.save(commit=False)
            issue.customer = request.user
            issue.save()
            return redirect('issue_success')  # Redirect to a success page or list of issues
    else:
        form = CustomerIssueForm()
    return render(request, 'customer/create_issues.html', {'form': form})

@login_required
def view_issues(request):
    issues = request.user.issues.all()  # Fetch issues of the logged-in user
    return render(request, 'customer/view_issues.html', {'issues': issues})



# Manager/views.py
from django.shortcuts import render, redirect
from Customer.models import CustomerIssue
@login_required
def notification_list(request):
    issues = CustomerIssue.objects.all().order_by('-id')
    return render(request, 'manager/manager_notif.html', {'issues': issues})

def mark_as_read(request, issue_id):
    issue = CustomerIssue.objects.get(id=issue_id)
    issue.is_read = True
    issue.save()
    return redirect('manager_notif')



from django.shortcuts import render
from Medadmin.models import Messege

def receive_messege(request):
    notifications = Messege.objects.all().order_by('-date')  # latest first
    return render(request, 'manager/receive_messege.html', {'notifications': notifications})


