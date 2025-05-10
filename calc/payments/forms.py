from django import forms
from django.contrib.auth.models import User
from .models import Advocate
from django.contrib.auth.hashers import make_password
from .validators import custom_username_validator  # Import custom validator

from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','username','password']  # Exclude username and date_joined


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()



class AdvocateForm(forms.ModelForm):
    class Meta:
        model = Advocate
        fields = ['mobile_number', 'date_of_birth', 'blood_group', 'enrolment_no','kawf_no', 'date_of_enrolment', 'due_amount', 'address', 'joined_date', 'picture']

class UserForm(forms.ModelForm):
    password = forms.CharField(validators=[custom_username_validator],widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ChangeUsernamePasswordForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="New Username")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("The passwords do not match.")
        return cleaned_data