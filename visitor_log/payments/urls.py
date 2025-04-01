from django.urls import path
from . import views

urlpatterns = [
    # Resident payment views
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
    
    # Admin views
    path('admin/dashboard/', views.admin_payment_dashboard, name='admin_payment_dashboard'),
    path('admin/export/', views.export_payments_csv, name='export_payments_csv'),
]