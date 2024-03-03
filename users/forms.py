from django import forms
from .models import Customer

class CustomUserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ['email', 'password']

        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_1', 'phone_2', 'address', 'CNPJ', 'contact_1', 'contact_2', 'contact_3', 'activity', 'status', 'image']