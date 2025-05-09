# payments/validators.py
from django.core.exceptions import ValidationError
import re

def custom_username_validator(value):
    # Allow alphanumeric, underscores, dashes, slashes, and dots
    if not re.match(r'^[\w/@./+-]+$', value):
        raise ValidationError('Enter a valid username. This value may contain only letters, numbers, @/./+/-/_ characters and slashes (/).')
