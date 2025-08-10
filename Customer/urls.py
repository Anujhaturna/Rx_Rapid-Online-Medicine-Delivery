from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.index, name='first_home'),
    path('home/', views.home_view, name='home_view'),
    path('start/', views.start_registration, name='start-registration'),
    path('register/', views.register_view, name='register'),
    path('create-account/', views.create_account, name='create-account'),
    path('login/', views.login_view, name='customer_login'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('resend-otp/', views.resend_otp_view, name='resend-otp'),

    path('customer_dashboard/', views.customer_dashboard, name='customer-dashboard'),
    path('upload-prescription/', views.upload_prescription, name='upload-prescription'),

    # 🆕 Non-prescription medicine flow
    path('non-prescription/', views.non_prescription, name='non-prescription'),
    path('non-prescription/browse/<int:store_id>/', views.browse_non_prescription, name='browse-non-prescription'),

#    path('non-prescription/upload/', views.upload_non_prescription_image, name='upload-non-prescription-image'),

    path('profile/', views.profile, name='profile'),
    path('medicines/', views.medicines_view, name='medicines'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('logout/', LogoutView.as_view(next_page='first_home'), name='logout'),
    path('api/search-stores/', views.search_medical_stores, name='search_stores'),
    path('add-to-cart/<int:medicine_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update-cart-quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('download-invoice/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('create_payment/<int:order_id>/', views.create_payment_order, name='create_payment'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),

    path('upload-confirm/', views.upload_prescription_confirm, name='upload-prescription-confirm'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('pay/<int:store_id>/', views.payment_gateway_integration, name='payment_gateway_integration'),
    path('process-online-method/', views.process_online_method, name='process-online-method'),
    path('contact/', views.contact_us, name='contact-us'),
    path('view-invoice/<int:prescription_id>/', views.view_invoice, name='view_invoice'),

    path('confirm-delivery/<int:prescription_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('create/', views.create_issue, name='customer-create-issue'),
    path('submitted/', views.issue_submitted, name='customer-issue-submitted'),
    path('about/', views.about_view, name='about'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
