from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class RentPayment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )
    
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rent_payments',
        limit_choices_to={'role': 'RESIDENT'}
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Rent payment for {self.resident.username} - {self.amount} ({self.get_status_display()})"
    
    @property
    def is_paid(self):
        return self.status == 'PAID'
    
    @property
    def is_pending(self):
        return self.status == 'PENDING'
    
    @property
    def is_failed(self):
        return self.status == 'FAILED'
