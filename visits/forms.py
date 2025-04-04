from django import forms
from django.contrib.auth import get_user_model
from .models import Visit

User = get_user_model()

class VisitRequestForm(forms.ModelForm):
    expected_arrival = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
        help_text="Select the expected arrival date and time"
    )

    class Meta:
        model = Visit
        fields = ['resident', 'visitor_name', 'visitor_phone', 'visitor_email', 'purpose', 'expected_arrival', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'purpose': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        security_guard = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only residents should be selectable
        self.fields['resident'].queryset = User.objects.filter(role='RESIDENT')
        self.fields['resident'].label_from_instance = lambda obj: f"{obj.username} ({obj.get_full_name()})"
        
        # Assign the form to the security guard who's creating it
        if security_guard:
            self.instance.requested_by = security_guard

    def clean(self):
        cleaned_data = super().clean()
        
        # Add blacklist check
        visitor_name = cleaned_data.get('visitor_name')
        visitor_phone = cleaned_data.get('visitor_phone')
        visitor_email = cleaned_data.get('visitor_email')
        
        if visitor_name:
            # Import locally to avoid circular import
            from reports.views import check_blacklist
            
            blacklist_entry = check_blacklist(
                visitor_name=visitor_name, 
                visitor_email=visitor_email,
                visitor_phone=visitor_phone
            )
            
            if blacklist_entry:
                raise forms.ValidationError(
                    f"This visitor is blacklisted: {blacklist_entry.reason}. "
                    f"Please contact an administrator for more information."
                )
        
        return cleaned_data


class VisitApprovalForm(forms.Form):
    APPROVAL_CHOICES = (
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
    )
    
    action = forms.ChoiceField(choices=APPROVAL_CHOICES, widget=forms.RadioSelect)
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Required if you're rejecting the request"
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'REJECT' and not rejection_reason:
            raise forms.ValidationError("Please provide a reason for rejecting the visit request.")
        
        return cleaned_data


class VisitFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All Status'),
    ) + Visit.STATUS_CHOICES
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    search = forms.CharField(required=False, max_length=100)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class VisitCheckInOutForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = []  # We don't need any fields here as we're just using buttons for actions 