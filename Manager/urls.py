from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('stores/', views.manage_stores, name='manage_stores'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('manager_profile/', views.manager_profile, name='manager_profile'),
    path('store/<int:store_id>/', views.view_store, name='view_store'),
    path('store/<int:store_id>/remove/', views.remove_store, name='remove_store'),
    path('manager_login', views.manager_login, name='manager_login'),
    path('store/<int:store_id>/prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('approve-store/<int:store_id>/', views.approve_store, name='approve_store'),
    path('reject-store/<int:store_id>/', views.reject_store, name='reject_store'),

    # ✅ Fixed names
    path('manager/send_notifications/', views.send_notifications, name='send_notifications'),
    path('manager/notifications_view/', views.sent_notifications, name='sent_notifications'),
    path('create/', views.create_issues, name='create_issues'),
    path('my-issues/', views.view_issues, name='view_issues'),
    path('manager_notif/', views.notification_list, name='manager_notif'),
    path('manager_notif/read/<int:issue_id>/', views.mark_as_read, name='manager-mark-as-read'),
    path('receive-messege/', views.receive_messege, name='receive_messege'),
]
