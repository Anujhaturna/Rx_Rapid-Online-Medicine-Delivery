from django.urls import path
from . import views

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('send-messege/', views.send_messege, name='send_messege'),
    path('view-reports/', views.view_reports, name='view_reports'),
    path('delete-prescription-bill/<int:bill_id>/', views.delete_prescription_bill, name='delete_prescription_bill'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
#     path('messege-success/', views.messege_success, name='messege_success'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-manager/<int:manager_id>/', views.delete_manager, name='delete_manager'),
    path('add-manager/', views.add_manager, name='add_manager'),
]
