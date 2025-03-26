from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'resident', 'purpose', 'status', 'requested_by', 'requested_at', 'entry_time', 'exit_time')
    list_filter = ('status', 'requested_at', 'entry_time', 'exit_time')
    search_fields = ('visitor_name', 'visitor_email', 'visitor_phone', 'purpose', 'resident__username', 'resident__first_name', 'resident__last_name', 'requested_by__username')
    readonly_fields = ('requested_at',)
    date_hierarchy = 'requested_at'
    fieldsets = (
        ('Visitor Information', {
            'fields': ('visitor_name', 'visitor_phone', 'visitor_email')
        }),
        ('Visit Details', {
            'fields': ('resident', 'purpose', 'notes', 'expected_arrival')
        }),
        ('Status Information', {
            'fields': ('status', 'requested_by', 'requested_at', 'approval_time', 'rejection_reason')
        }),
        ('Check In/Out', {
            'fields': ('entry_time', 'exit_time')
        }),
    )
