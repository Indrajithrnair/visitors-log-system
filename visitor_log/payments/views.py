import json
import razorpay
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import datetime, timedelta
from users.views import role_required
from .models import RentPayment
from .forms import RentPaymentForm, RentPaymentDateFilterForm
from django.db.models.functions import TruncDate

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def payment_dashboard(request):
    """Dashboard showing payment history for residents."""
    user = request.user
    
    # Get payments based on user role
    if user.role == 'RESIDENT':
        payments = RentPayment.objects.filter(resident=user).order_by('-payment_date')
        # Calculate pending amount if any unpaid payments
        pending_amount = payments.filter(status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
        # Get next due date (closest future due date)
        today = timezone.now().date()
        next_payment = payments.filter(due_date__gte=today).order_by('due_date').first()
        
        return render(request, 'payments/dashboard.html', {
            'payments': payments,
            'pending_amount': pending_amount,
            'next_payment': next_payment,
            'title': 'Payment Dashboard'
        })
    elif user.role == 'ADMIN':
        # Redirect admins to the admin payment dashboard
        return redirect('admin_payment_dashboard')
    else:
        # Handle security guards or other roles
        messages.error(request, "You don't have access to the payment dashboard.")
        return redirect('dashboard')

@login_required
@role_required(['RESIDENT'])
def initiate_payment(request):
    """View to initiate a new rent payment."""
    if request.method == 'POST':
        form = RentPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.resident = request.user
            payment.status = 'PENDING'
            payment.save()
            
            # Create Razorpay Order
            amount_in_paise = int(payment.amount * 100)  # Convert to paise
            
            order_data = {
                'amount': amount_in_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'receipt': f'order_rcpt_{payment.id}',
                'notes': {
                    'payment_id': str(payment.id),
                    'resident_id': str(payment.resident.id)
                }
            }
            
            razorpay_order = client.order.create(data=order_data)
            payment.order_id = razorpay_order['id']
            payment.save()
            
            # Prepare payment data for frontend
            payment_data = {
                'key': settings.RAZORPAY_KEY_ID,
                'amount': amount_in_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'name': settings.RAZORPAY_COMPANY_NAME,
                'description': f'Rent Payment for {request.user.username}',
                'order_id': razorpay_order['id'],
                'callback_url': request.build_absolute_uri(reverse('payment_callback')),
                'prefill': {
                    'name': f"{request.user.first_name} {request.user.last_name}",
                    'email': request.user.email,
                }
            }
            
            return render(request, 'payments/payment_process.html', {
                'payment': payment,
                'payment_data': payment_data,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'title': 'Process Payment'
            })
    else:
        # Set default amount (could be fetched from resident profile)
        form = RentPaymentForm(initial={'amount': 10000.00})  # Default Rs. 10,000
    
    return render(request, 'payments/payment_form.html', {
        'form': form,
        'title': 'Make Rent Payment'
    })

@csrf_exempt
def payment_callback(request):
    """Handle the Razorpay payment callback."""
    if request.method == 'POST':
        try:
            # Get the payment ID and order ID
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            # Verify the payment signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)
            
            # Find the payment record
            payment = RentPayment.objects.get(order_id=order_id)
            payment.payment_id = payment_id
            payment.transaction_id = payment_id  # Using payment_id as transaction_id
            payment.status = 'PAID'
            payment.save()
            
            # Send email confirmation
            try:
                _send_payment_confirmation_email(payment)
            except Exception as e:
                # Log the error but don't stop the process
                print(f"Error sending confirmation email: {str(e)}")
            
            messages.success(request, "Payment successful! Your rent payment has been recorded.")
            return redirect('payment_success', payment_id=payment.id)
            
        except Exception as e:
            # Payment verification failed
            if order_id:
                try:
                    payment = RentPayment.objects.get(order_id=order_id)
                    payment.status = 'FAILED'
                    payment.notes = str(e)
                    payment.save()
                except RentPayment.DoesNotExist:
                    pass
            
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect('payment_failure')
    
    return redirect('payment_dashboard')

@login_required
def payment_success(request, payment_id):
    """Show payment success page."""
    payment = get_object_or_404(RentPayment, id=payment_id)
    
    # Only allow the resident who made the payment to see their success page
    if request.user != payment.resident and request.user.role != 'ADMIN':
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('dashboard')
    
    return render(request, 'payments/payment_success.html', {
        'payment': payment,
        'title': 'Payment Successful'
    })

@login_required
def payment_failure(request):
    """Show payment failure page."""
    return render(request, 'payments/payment_failure.html', {
        'title': 'Payment Failed'
    })

@login_required
@role_required(['ADMIN'])
def admin_payment_dashboard(request):
    """Admin dashboard for viewing all payments."""
    # Process filter form
    form = RentPaymentDateFilterForm(request.GET)
    payments = RentPayment.objects.all()
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        status = form.cleaned_data.get('status')
        
        if start_date:
            payments = payments.filter(payment_date__date__gte=start_date)
        if end_date:
            payments = payments.filter(payment_date__date__lte=end_date)
        if status:
            payments = payments.filter(status=status)
    
    # Calculate summary statistics
    total_amount = payments.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
    total_payments = payments.filter(status='PAID').count()
    pending_amount = payments.filter(status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = payments.filter(status='PENDING').count()
    
    # Get the last 30 days of payments for the chart
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_payments = payments.filter(payment_date__gte=thirty_days_ago)
    
    # Group by day for the chart
    payment_data = (
        recent_payments
        .annotate(day=TruncDate('payment_date'))
        .values('day')
        .annotate(count=Count('id'), total=Sum('amount'))
        .order_by('day')
    )
    
    # Prepare the data for the chart
    dates = [item['day'].strftime('%Y-%m-%d') for item in payment_data]
    amounts = [float(item['total']) for item in payment_data]
    
    return render(request, 'payments/admin_dashboard.html', {
        'payments': payments,
        'form': form,
        'total_amount': total_amount,
        'total_payments': total_payments,
        'pending_amount': pending_amount,
        'pending_payments': pending_payments,
        'chart_dates': json.dumps(dates),
        'chart_amounts': json.dumps(amounts),
        'title': 'Payment Administration'
    })

@login_required
@role_required(['ADMIN'])
def export_payments_csv(request):
    """Export payments data as CSV."""
    # Process filters if any
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    
    payments = RentPayment.objects.all()
    
    if start_date:
        payments = payments.filter(payment_date__date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__date__lte=end_date)
    if status:
        payments = payments.filter(status=status)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="rent_payments_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    # Write CSV data
    import csv
    writer = csv.writer(response)
    writer.writerow([
        'Payment ID', 'Resident', 'Amount', 'Status', 'Transaction ID',
        'Payment Date', 'Due Date', 'Notes'
    ])
    
    for payment in payments:
        writer.writerow([
            payment.id,
            payment.resident.username,
            payment.amount,
            payment.get_status_display(),
            payment.transaction_id or 'N/A',
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            payment.due_date.strftime('%Y-%m-%d') if payment.due_date else 'N/A',
            payment.notes or 'N/A'
        ])
    
    return response

def _send_payment_confirmation_email(payment):
    """Helper function to send payment confirmation email."""
    subject = 'Your Rent Payment Confirmation'
    template = 'payments/email/payment_confirmation.html'
    
    context = {
        'payment': payment,
        'user': payment.resident,
        'company_name': settings.RAZORPAY_COMPANY_NAME
    }
    
    message = render_to_string(template, context)
    to_email = payment.resident.email
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        html_message=message,
        fail_silently=False
    )