from django.db import models
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Visit(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELLED', 'Cancelled'),
    )
    
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='resident_visits',
        limit_choices_to={'role': 'RESIDENT'}
    )
    visitor_name = models.CharField(max_length=100)
    visitor_phone = models.CharField(max_length=20, blank=True, null=True)
    visitor_email = models.EmailField(blank=True, null=True)
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='requested_visits',
        limit_choices_to={'role': 'SECURITY'},
        null=True,  # Make this field optional to fix the issue
        blank=True
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    expected_arrival = models.DateTimeField(null=True, blank=True)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    approval_time = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.visitor_name} - Visit to {self.resident.username}"
    
    def save(self, *args, **kwargs):
        if not self.requested_by_id:
            logger.error("Visit is being saved without a requested_by user set")
            print("Visit is being saved without a requested_by user set")
            
            # Try to find a security user to fill in as a fallback
            from django.contrib.auth import get_user_model
            User = get_user_model()
            security_user = User.objects.filter(role='SECURITY').first()
            if security_user:
                print(f"Using fallback security user: {security_user.username}")
                self.requested_by = security_user
        
        print(f"Saving visit: ID={self.id or 'New'}, "
              f"Visitor={self.visitor_name}, "
              f"Resident={self.resident.username if self.resident_id else 'None'}, "
              f"Requested by={self.requested_by.username if self.requested_by_id else 'None'}")
        
        logger.info(f"Saving visit: ID={self.id or 'New'}, "
                  f"Visitor={self.visitor_name}, "
                  f"Resident={self.resident.username if self.resident_id else 'None'}, "
                  f"Requested by={self.requested_by.username if self.requested_by_id else 'None'}")
        
        super().save(*args, **kwargs)
        logger.info(f"Visit saved successfully with ID={self.id}")
        print(f"Visit saved successfully with ID={self.id}")
    
    def approve(self):
        self.status = 'APPROVED'
        self.approval_time = timezone.now()
        self.save()
    
    def reject(self, reason=None):
        self.status = 'REJECTED'
        if reason:
            self.rejection_reason = reason
        self.approval_time = timezone.now()
        self.save()
    
    def check_in(self):
        self.status = 'CHECKED_IN'
        self.entry_time = timezone.now()
        self.save()
    
    def check_out(self):
        self.status = 'CHECKED_OUT'
        self.exit_time = timezone.now()
        self.save()
    
    def cancel(self):
        self.status = 'CANCELLED'
        self.save()
    
    class Meta:
        ordering = ['-requested_at']
