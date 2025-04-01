from django import forms
from .models import RentPayment
from django.core.validators import MinValueValidator

class RentPaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(100)],  # Minimum payment amount
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = RentPayment
        fields = ['amount', 'notes']
        
class RentPaymentDateFilterForm(forms.Form):
    """Form for filtering payments by date range."""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + list(RentPayment.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )