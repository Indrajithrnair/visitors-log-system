from django import forms
from django.contrib.auth import get_user_model
from .models import Visit
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
import traceback
import sys

logger = logging.getLogger(__name__)

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
            logger.debug(f"Setting requested_by to security guard: {security_guard.username} (ID: {security_guard.id})")
            self.instance.requested_by = security_guard
            # Force print to console for immediate feedback
            print(f"Setting requested_by to security guard: {security_guard.username} (ID: {security_guard.id})")
        else:
            logger.error("No security guard user provided to the form")
            print("ERROR: No security guard user provided to the form")

    def clean_expected_arrival(self):
        expected_arrival = self.cleaned_data.get('expected_arrival')
        now = timezone.now()
        
        if expected_arrival and expected_arrival <= now:
            # Add a more specific message depending on how close the time is to now
            time_diff = expected_arrival - now
            if time_diff.days < 0:
                raise ValidationError("Expected arrival date must be in the future.")
            else:
                raise ValidationError("Expected arrival time must be at least a few minutes in the future.")
            
        return expected_arrival
    
    def save(self, commit=True):
        try:
            # Print to console for immediate feedback
            print("======= ATTEMPTING TO SAVE VISIT =======")
            logger.debug("Attempting to save visit")
            
            # Log all form data for debugging
            print(f"FORM DATA: {self.cleaned_data}")
            logger.debug(f"Form cleaned_data: {self.cleaned_data}")
            
            resident = self.cleaned_data.get('resident')
            visitor_name = self.cleaned_data.get('visitor_name')
            purpose = self.cleaned_data.get('purpose')
            expected_arrival = self.cleaned_data.get('expected_arrival')
            
            print(f"Visit details: Resident={resident.username if resident else 'None'} (ID: {resident.id if resident else 'None'})")
            print(f"Visitor={visitor_name}, Purpose={purpose}")
            print(f"Expected arrival: {expected_arrival}")
            
            # Ensure requested_by is set
            if not hasattr(self.instance, 'requested_by') or not self.instance.requested_by:
                # This is likely the issue - requested_by is not being set
                print("ERROR: requested_by is not set on the form instance")
                logger.error("requested_by is not set on the form instance")
                
                # Try to get the current user from somewhere else
                from django.contrib.auth.models import AnonymousUser
                if hasattr(self, 'request') and hasattr(self.request, 'user') and not isinstance(self.request.user, AnonymousUser):
                    self.instance.requested_by = self.request.user
                    print(f"Set requested_by from request: {self.request.user.username}")
                else:
                    # Try to find a security guard in the system
                    security_users = User.objects.filter(role='SECURITY').first()
                    if security_users:
                        self.instance.requested_by = security_users
                        print(f"Set requested_by to first security guard: {security_users.username}")
                    else:
                        print("ERROR: Could not find any security users to set as requested_by")
                        return None
            else:
                print(f"requested_by is correctly set to: {self.instance.requested_by.username} (ID: {self.instance.requested_by.id})")
                
            # Make sure resident is set
            if not resident:
                print("ERROR: No resident selected")
                logger.error("No resident selected")
                return None
                
            # Force set all the required fields directly
            self.instance.resident = resident
            self.instance.visitor_name = visitor_name
            self.instance.purpose = purpose
            self.instance.expected_arrival = expected_arrival
            
            # Save and log the result
            print("Calling super().save()")
            visit = super().save(commit=commit)
            print(f"Visit saved successfully: ID={visit.id}")
            logger.debug(f"Visit saved successfully: {visit}")
            
            # Double check that the visit was created
            try:
                saved_visit = Visit.objects.get(id=visit.id)
                print(f"Confirmed visit in database: ID={saved_visit.id}, Resident={saved_visit.resident.username}, Requested by={saved_visit.requested_by.username}")
            except Visit.DoesNotExist:
                print(f"ERROR: Visit with ID {visit.id} does not exist in database after save!")
                
            return visit
        except Exception as e:
            print(f"ERROR saving visit: {str(e)}")
            print(f"Exception type: {type(e)}")
            print("Traceback:")
            traceback.print_exc(file=sys.stdout)
            logger.error(f"Error saving visit: {str(e)}")
            raise
    
    # NOTE: Blacklist check code has been completely removed


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