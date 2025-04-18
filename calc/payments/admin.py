from django.contrib import admin
from .models import Advocate,Payment,MonthlyPaymentDue
from django.contrib.auth.models import User



admin.site.register(Advocate)
admin.site.register(Payment)
admin.site.register(MonthlyPaymentDue)