from django.urls import path
from . import views

app_name = 'medical'

urlpatterns = [
    path('medical_registration/', views.medical_registration, name='medical_registration'),
    path('medical_login/', views.medical_login, name='medical_login'),
    path('medical_dashboard/', views.medical_dashboard, name='medical_dashboard'),  # After login
    path('logout/', views.medical_logout, name='logout'),  # Logout
    path('add_medicine/', views.add_medicine, name='add_medicine'),
    path('view-uploaded-prescriptions/', views.view_uploaded_prescriptions, name='view_uploaded_prescriptions'),
    path('prescription/<int:prescription_id>/generate-bill/', views.view_prescription_and_generate_bill, name='view_prescription_and_generate_bill'),
    path('notify-patient/<int:bill_id>/', views.notify_patient, name='notify_patient'),
    # path('order/<int:order_id>/confirm/', views.confirm_order_view, name='confirm_order'),
    # path('order/<int:order_id>/approve/', views.approve_order, name='approve_order'),
    # path('customer-documents/<int:customer_id>/', views.customer_documents_view, name='customer_documents'),
    path('customer/<int:customer_id>/prescriptions/', views.customer_prescriptions_view, name='customer_prescriptions'),
    path('non-prescription-orders/', views.view_non_prescription_orders, name='view_non_prescription_orders'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('medical_store_notifications', views.medical_store_notifications, name='medical_store_notifications'),
    path('medicine/edit/<int:medicine_id>/', views.edit_medicine, name='edit_medicine'),
    path('medicine/delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),



]