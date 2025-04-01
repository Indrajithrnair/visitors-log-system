from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Report, Blacklist
from .forms import ReportForm, BlacklistForm
from visits.models import Visit
from users.views import role_required

@login_required
def report_visitor(request, visit_id=None):
    """
    View for residents or security guards to report suspicious visitors
    """
    # Can be called with specific visit_id or without
    if visit_id:
        visit = get_object_or_404(Visit, pk=visit_id)
        
        # Security guards can report any visit, but residents can only report their own
        if request.user.role == 'RESIDENT' and visit.resident != request.user:
            messages.error(request, "You can only report visitors for your own visits.")
            return redirect('resident_visit_requests')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user, visit_id=visit_id)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.save()
            
            messages.success(request, "Visitor has been reported. An administrator will review the report.")
            
            # Redirect based on user role
            if request.user.role == 'RESIDENT':
                return redirect('resident_visit_requests')
            else:
                return redirect('visit_list')
    else:
        form = ReportForm(user=request.user, visit_id=visit_id)
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'title': 'Report Suspicious Visitor'
    })


@login_required
@role_required(['ADMIN'])
def report_list(request):
    """
    Admin view to see all reports
    """
    # Get search parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    reports = Report.objects.all()
    
    # Apply filters
    if search:
        reports = reports.filter(
            Q(visit__visitor_name__icontains=search) |
            Q(reported_by__username__icontains=search) |
            Q(reason__icontains=search)
        )
    
    if status == 'reviewed':
        reports = reports.filter(reviewed=True)
    elif status == 'unreviewed':
        reports = reports.filter(reviewed=False)
    
    # Paginate results
    paginator = Paginator(reports.order_by('-created_at'), 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reports/report_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'title': 'Visitor Reports'
    })


@login_required
@role_required(['ADMIN'])
def report_detail(request, pk):
    """
    Admin view to see report details and take action
    """
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark_reviewed':
            report.reviewed = True
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            messages.success(request, "Report marked as reviewed.")
            return redirect('report_list')
        
        elif action == 'blacklist':
            # Redirect to blacklist form pre-filled with this report
            return redirect('create_blacklist', report_id=report.pk)
    
    # Check if visitor is already blacklisted
    is_blacklisted = Blacklist.objects.filter(
        visitor_name=report.visit.visitor_name,
        is_active=True
    ).exists()
    
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'is_blacklisted': is_blacklisted,
        'title': f'Report on {report.visit.visitor_name}'
    })


@login_required
@role_required(['ADMIN'])
def create_blacklist(request, report_id=None):
    """
    Admin view to blacklist a visitor, optionally based on a report
    """
    report = None
    if report_id:
        report = get_object_or_404(Report, pk=report_id)
    
    if request.method == 'POST':
        form = BlacklistForm(request.POST, report=report)
        if form.is_valid():
            blacklist = form.save(commit=False)
            blacklist.blacklisted_by = request.user
            
            # Link to report if applicable
            report_id = form.cleaned_data.get('report_id')
            if report_id:
                blacklist.related_report = get_object_or_404(Report, pk=report_id)
            
            blacklist.save()
            messages.success(request, f"{blacklist.visitor_name} has been added to the blacklist.")
            
            # If from a report, mark it as reviewed
            if report:
                report.reviewed = True
                report.reviewed_by = request.user
                report.reviewed_at = timezone.now()
                report.save()
            
            return redirect('blacklist_list')
    else:
        form = BlacklistForm(report=report, report_id=report_id)
    
    return render(request, 'reports/blacklist_form.html', {
        'form': form,
        'report': report,
        'title': 'Add to Blacklist'
    })


@login_required
@role_required(['ADMIN', 'SECURITY'])
def blacklist_list(request):
    """
    View to see all blacklisted visitors
    """
    # Get search parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', 'active')
    
    blacklist = Blacklist.objects.all()
    
    # Apply filters
    if search:
        blacklist = blacklist.filter(
            Q(visitor_name__icontains=search) |
            Q(visitor_email__icontains=search) |
            Q(visitor_phone__icontains=search) |
            Q(reason__icontains=search)
        )
    
    if status == 'active':
        blacklist = blacklist.filter(is_active=True)
    elif status == 'inactive':
        blacklist = blacklist.filter(is_active=False)
    
    # Paginate results
    paginator = Paginator(blacklist.order_by('-created_at'), 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Different context based on user role
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'title': 'Visitor Blacklist'
    }
    
    # Admins can manage blacklist, security guards can only view
    context['is_admin'] = request.user.role == 'ADMIN'
    
    return render(request, 'reports/blacklist_list.html', context)


@login_required
@role_required(['ADMIN'])
def blacklist_detail(request, pk):
    """
    Admin view to see blacklist details and take action
    """
    blacklist = get_object_or_404(Blacklist, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'deactivate':
            blacklist.is_active = False
            blacklist.save()
            messages.success(request, f"{blacklist.visitor_name} has been removed from the active blacklist.")
        
        elif action == 'activate':
            blacklist.is_active = True
            blacklist.save()
            messages.success(request, f"{blacklist.visitor_name} has been added back to the active blacklist.")
        
        elif action == 'edit':
            return redirect('edit_blacklist', pk=blacklist.pk)
        
        return redirect('blacklist_list')
    
    return render(request, 'reports/blacklist_detail.html', {
        'blacklist': blacklist,
        'title': f'Blacklist: {blacklist.visitor_name}'
    })


@login_required
@role_required(['ADMIN'])
def edit_blacklist(request, pk):
    """
    Admin view to edit blacklist entry
    """
    blacklist = get_object_or_404(Blacklist, pk=pk)
    
    if request.method == 'POST':
        form = BlacklistForm(request.POST, instance=blacklist)
        if form.is_valid():
            form.save()
            messages.success(request, "Blacklist entry updated successfully.")
            return redirect('blacklist_detail', pk=blacklist.pk)
    else:
        form = BlacklistForm(instance=blacklist)
    
    return render(request, 'reports/blacklist_form.html', {
        'form': form,
        'blacklist': blacklist,
        'title': 'Edit Blacklist Entry'
    })


@login_required
@role_required(['ADMIN'])
def delete_from_blacklist(request, pk):
    """
    Admin view to remove a visitor from blacklist
    """
    blacklist_entry = get_object_or_404(Blacklist, pk=pk)
    
    if request.method == 'POST':
        visitor_name = blacklist_entry.visitor_name
        blacklist_entry.delete()
        messages.success(request, f"{visitor_name} has been removed from the blacklist.")
        return redirect('blacklist_list')
        
    return render(request, 'reports/delete_blacklist_confirm.html', {
        'blacklist': blacklist_entry,
        'title': 'Remove from Blacklist'
    })


# Hook into visit request creation to check blacklist
def check_blacklist(visitor_name, visitor_email=None, visitor_phone=None):
    """
    Utility function to check if a visitor is blacklisted
    Returns the blacklist entry if found, None otherwise
    """
    blacklist_query = Q(visitor_name__iexact=visitor_name, is_active=True)
    
    if visitor_email:
        blacklist_query |= Q(visitor_email__iexact=visitor_email, is_active=True)
    
    if visitor_phone:
        blacklist_query |= Q(visitor_phone__iexact=visitor_phone, is_active=True)
    
    try:
        return Blacklist.objects.filter(blacklist_query).first()
    except:
        return None
