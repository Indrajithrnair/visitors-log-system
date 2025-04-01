from django.contrib import admin
from .models import RentPayment

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('resident', 'amount', 'status', 'payment_date', 'due_date', 'transaction_id')
    list_filter = ('status', 'payment_date', 'due_date')
    search_fields = ('resident__username', 'resident__email', 'transaction_id')
    readonly_fields = ('payment_date', 'updated_at')
    fieldsets = (
        ('Resident Information', {
            'fields': ('resident',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'status', 'due_date')
        }),
        ('Transaction Information', {
            'fields': ('transaction_id', 'payment_id', 'order_id', 'notes')
        }),
        ('Dates', {
            'fields': ('payment_date', 'updated_at')
        }),
    )
