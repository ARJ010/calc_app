from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Advocate)
admin.site.register(Payment)
admin.site.register(MonthlyPaymentDue)


