from django import forms
from django.contrib.auth.models import User
from .models import Advocate
from django.contrib.auth.hashers import make_password


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()



class AdvocateForm(forms.ModelForm):
    class Meta:
        model = Advocate
        fields = ['mobile_number', 'date_of_birth', 'blood_group', 'enrolment_no','kawf_no', 'date_of_enrolment', 'bar_registration', 'due_amount', 'address', 'joined_date', 'picture']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
