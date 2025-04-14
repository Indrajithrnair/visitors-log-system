from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import logging
import sys
import traceback

from .models import Visit
from .forms import VisitRequestForm, VisitApprovalForm, VisitFilterForm, VisitCheckInOutForm
from users.views import role_required

# Set up logging
logger = logging.getLogger(__name__)

@login_required
@role_required(['SECURITY'])
def create_visit_request(request):
    print(f"DEBUG: User {request.user.username} (role: {request.user.role}) is attempting to create a visit request")
    
    if request.method == 'POST':
        print(f"DEBUG: POST data received: {dict(request.POST)}")
        
        try:
            form = VisitRequestForm(request.POST, user=request.user)
            
            if form.is_valid():
                print("DEBUG: Form is valid, saving visit")
                
                # Make sure the user is correctly set
                form.instance.requested_by = request.user
                print(f"DEBUG: Manually set requested_by to {request.user.username} (ID: {request.user.id})")
                
                try:
                    visit = form.save()
                    
                    if visit and hasattr(visit, 'id'):
                        print(f"DEBUG: Visit created successfully: ID={visit.id}, Visitor={visit.visitor_name}, Resident={visit.resident.username}")
                        messages.success(request, f"Visit request for {visit.visitor_name} has been created successfully.")
                        return redirect('visit_list')
                    else:
                        print("DEBUG ERROR: Visit was not created or has no ID")
                        messages.error(request, "An error occurred while creating the visit request. Please try again.")
                except Exception as e:
                    print(f"DEBUG EXCEPTION saving form: {str(e)}")
                    traceback.print_exc(file=sys.stdout)
                    messages.error(request, f"Error creating visit: {str(e)}")
            else:
                print(f"DEBUG: Form validation failed: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        except Exception as e:
            print(f"DEBUG EXCEPTION in create_visit_request: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    else:
        form = VisitRequestForm(user=request.user)
    
    return render(request, 'visits/create_visit.html', {
        'form': form,
        'title': 'Create Visit Request'
    })


@login_required
@role_required(['SECURITY'])
def visit_list(request):
    form = VisitFilterForm(request.GET)
    visits = Visit.objects.all()
    
    if form.is_valid():
        status = form.cleaned_data.get('status')
        from_date = form.cleaned_data.get('from_date')
        to_date = form.cleaned_data.get('to_date')
        search = form.cleaned_data.get('search')
        
        if status:
            visits = visits.filter(status=status)
        
        if from_date:
            visits = visits.filter(requested_at__date__gte=from_date)
        
        if to_date:
            visits = visits.filter(requested_at__date__lte=to_date)
            
        if search:
            visits = visits.filter(
                Q(visitor_name__icontains=search) | 
                Q(purpose__icontains=search) |
                Q(resident__username__icontains=search) |
                Q(resident__first_name__icontains=search) |
                Q(resident__last_name__icontains=search)
            )
    
    paginator = Paginator(visits, 10)  # Show 10 visits per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'visits/visit_list.html', {
        'page_obj': page_obj,
        'filter_form': form,
        'title': 'All Visit Requests'
    })


@login_required
@role_required(['RESIDENT'])
def resident_visit_requests(request):
    form = VisitFilterForm(request.GET)
    visits = Visit.objects.filter(resident=request.user)
    
    if form.is_valid():
        status = form.cleaned_data.get('status')
        from_date = form.cleaned_data.get('from_date')
        to_date = form.cleaned_data.get('to_date')
        search = form.cleaned_data.get('search')
        
        if status:
            visits = visits.filter(status=status)
        
        if from_date:
            visits = visits.filter(requested_at__date__gte=from_date)
        
        if to_date:
            visits = visits.filter(requested_at__date__lte=to_date)
            
        if search:
            visits = visits.filter(
                Q(visitor_name__icontains=search) | 
                Q(purpose__icontains=search)
            )
    
    pending_visits = visits.filter(status='PENDING').count()
    
    paginator = Paginator(visits, 10)  # Show 10 visits per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'visits/resident_visits.html', {
        'page_obj': page_obj,
        'filter_form': form,
        'title': 'My Visit Requests',
        'pending_visits': pending_visits
    })


@login_required
@role_required(['RESIDENT'])
def approve_reject_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk, resident=request.user, status='PENDING')
    
    if request.method == 'POST':
        form = VisitApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action')
            rejection_reason = form.cleaned_data.get('rejection_reason')
            
            if action == 'APPROVE':
                visit.approve()
                messages.success(request, f"Visit request for {visit.visitor_name} has been approved.")
            else:
                visit.reject(rejection_reason)
                messages.success(request, f"Visit request for {visit.visitor_name} has been rejected.")
                
            return redirect('resident_visit_requests')
    else:
        form = VisitApprovalForm()
    
    return render(request, 'visits/approve_reject_visit.html', {
        'visit': visit,
        'form': form,
        'title': 'Approve or Reject Visit'
    })


@login_required
@role_required(['SECURITY'])
def visit_detail(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    return render(request, 'visits/visit_detail.html', {
        'visit': visit,
        'title': f'Visit: {visit.visitor_name}'
    })


@login_required
@role_required(['SECURITY'])
def check_in_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk, status='APPROVED')
    visit.check_in()
    messages.success(request, f"{visit.visitor_name} has been checked in.")
    return redirect('visit_detail', pk=pk)


@login_required
@role_required(['SECURITY'])
def check_out_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk, status='CHECKED_IN')
    visit.check_out()
    messages.success(request, f"{visit.visitor_name} has been checked out.")
    return redirect('visit_detail', pk=pk)
