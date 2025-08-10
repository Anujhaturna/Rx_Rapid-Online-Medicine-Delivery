from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MessegeForm
from .models import Messege

# Static admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            return redirect('admin_dashboard')
        else:
            return render(request, 'Medadmin/admin_login.html', {'error': 'Invalid credentials'})

    return render(request, 'Medadmin/admin_login.html')


def admin_dashboard(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')

    return render(request, 'Medadmin/admin_dashboard.html')  # Create this templates


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')



from django.shortcuts import render, redirect
from .forms import MessegeForm
from .models import Messege

def send_messege(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            Messege.objects.filter(id=request.POST.get('delete_id')).delete()
            return redirect('send_messege')  # Replace with your URL name
        else:
            form = MessegeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('send_messege')  # Replace with your URL name
    else:
        form = MessegeForm()

    all_messages = Messege.objects.all().order_by('-date')
    return render(request, 'Medadmin/send_messege.html', {
        'form': form,
        'all_messages': all_messages
    })

# from django.http import HttpResponse
#
# def messege_success(request):
#     return HttpResponse('<h2>Notification sent successfully!</h2><a href="/send-messege/">Send another</a> | <a href="/receive-messages/">View Messages</a>')
#
#
#



from medical.models import PrescriptionBill
from Customer.models import Order


from django.db.models.functions import TruncMonth
from django.db.models import Sum
from collections import defaultdict
from django.shortcuts import render
import json
from Customer.models import Order
from medical.models import PrescriptionBill, MediRegistration
from decimal import Decimal


def view_reports(request):
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
    return render(request, 'Medadmin/view_reports.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_prescription_bill(request, bill_id):
    if request.method == "POST":
        bill = get_object_or_404(PrescriptionBill, id=bill_id)
        bill.delete()
        messages.success(request, "Prescription bill deleted successfully.")
    return redirect('view_reports')


def delete_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.success(request, "Order deleted successfully.")
    return redirect('view_reports')


# admin/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from Manager.models import ManagerProfile
from medical.models import MediRegistration

User = get_user_model()

def manage_users(request):
    query = request.GET.get('q', '').strip()

    customers = User.objects.filter(manager_profile__isnull=True)
    stores = MediRegistration.objects.all()
    managers = ManagerProfile.objects.select_related('user').all()

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query)
        )
        stores = stores.filter(
            Q(store_name__icontains=query) |
            Q(email__icontains=query) |
            Q(owner_name__icontains=query) |
            Q(pharmacist_name__icontains=query) |
            Q(address__icontains=query)
        )

    context = {
        'customers': customers,
        'stores': stores,
        'managers': managers,
        'query': query
    }

    # ✅ If AJAX, return only the partial HTML
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'Medadmin/manage_users_tables.html', context)

    # ✅ Normal: return the full page
    return render(request, 'Medadmin/manage_users.html', context)



def delete_manager(request, manager_id):
    manager = get_object_or_404(ManagerProfile, id=manager_id)
    user = manager.user
    manager.delete()
    user.delete()  # also remove login account
    return redirect('manage_users')


from django import forms
from django.contrib.auth.hashers import make_password

class AddManagerForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

def add_manager(request):
    if request.method == 'POST':
        form = AddManagerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create user
            user = User.objects.create(
                email=data['email'],
                phone=data['phone_number'],
                name=f"{data['first_name']} {data['last_name']}",
                password=make_password(data['password'])
            )

            # Create profile
            ManagerProfile.objects.create(
                user=user,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone_number']
            )

            return redirect('manage_users')

    else:
        form = AddManagerForm()

    return render(request, 'Medadmin/add_manager.html', {'form': form})


