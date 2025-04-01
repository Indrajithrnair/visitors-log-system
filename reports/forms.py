from django import forms
from .models import Report, Blacklist
from visits.models import Visit

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['visit', 'reason', 'severity']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        visit_id = kwargs.pop('visit_id', None)
        super().__init__(*args, **kwargs)
        
        # If a specific visit is being reported, pre-select it
        if visit_id:
            self.fields['visit'].initial = visit_id
            self.fields['visit'].widget = forms.HiddenInput()
        else:
            # Only show visits relevant to the user based on their role
            if user and user.role == 'RESIDENT':
                self.fields['visit'].queryset = Visit.objects.filter(resident=user)
            elif user and user.role == 'SECURITY':
                self.fields['visit'].queryset = Visit.objects.all()


class BlacklistForm(forms.ModelForm):
    report_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Blacklist
        fields = ['visitor_name', 'visitor_phone', 'visitor_email', 'reason', 'expires_at', 'notes']
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'visitor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'visitor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        report_id = kwargs.pop('report_id', None)
        report = kwargs.pop('report', None)
        super().__init__(*args, **kwargs)
        
        if report_id:
            self.fields['report_id'].initial = report_id
        
        # Pre-fill form with data from report if available
        if report:
            self.fields['visitor_name'].initial = report.visit.visitor_name
            self.fields['visitor_phone'].initial = report.visit.visitor_phone if hasattr(report.visit, 'visitor_phone') else ''
            self.fields['visitor_email'].initial = report.visit.visitor_email if hasattr(report.visit, 'visitor_email') else ''
            self.fields['reason'].initial = f"Blacklisted based on report: {report.reason}" 