from django.db import models
from django.conf import settings
from visits.models import Visit

class Report(models.Model):
    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )
    
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='reported_visitors'
    )
    visit = models.ForeignKey(
        Visit, 
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reason = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report on {self.visit.visitor_name} by {self.reported_by.username}"
    
    class Meta:
        ordering = ['-created_at']


class Blacklist(models.Model):
    visitor_name = models.CharField(max_length=100)
    visitor_phone = models.CharField(max_length=20, blank=True, null=True)
    visitor_email = models.EmailField(blank=True, null=True)
    reason = models.TextField()
    blacklisted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blacklisted_visitors'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    related_report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blacklist_entries'
    )
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Blacklisted: {self.visitor_name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Blacklist Entries"
