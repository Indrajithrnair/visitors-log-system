from django.contrib import admin
from .models import Report, Blacklist

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('visit', 'visitor_name', 'reported_by', 'severity', 'created_at', 'reviewed')
    list_filter = ('severity', 'reviewed', 'created_at')
    search_fields = ('visit__visitor_name', 'reported_by__username', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def visitor_name(self, obj):
        return obj.visit.visitor_name
    
    actions = ['mark_as_reviewed']
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(reviewed=True, reviewed_by=request.user)
    mark_as_reviewed.short_description = "Mark selected reports as reviewed"


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'visitor_email', 'visitor_phone', 'blacklisted_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('visitor_name', 'visitor_email', 'visitor_phone', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    actions = ['activate_blacklist', 'deactivate_blacklist']
    
    def activate_blacklist(self, request, queryset):
        queryset.update(is_active=True)
    activate_blacklist.short_description = "Activate selected blacklist entries"
    
    def deactivate_blacklist(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_blacklist.short_description = "Deactivate selected blacklist entries"
