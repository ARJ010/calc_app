from django import forms
from django.contrib.auth.models import User
from .models import Advocate
from django.contrib.auth.hashers import make_password

class AdvocateCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")
