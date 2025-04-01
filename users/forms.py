from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, 
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username
        
        if email and CustomUser.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('A user with that email already exists.')
            
        return email 