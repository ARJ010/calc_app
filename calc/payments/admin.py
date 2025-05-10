from django.contrib import admin
from .models import Advocate, Payment, MonthlyPaymentDue

@admin.register(Advocate)
class AdvocateAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrolment_no', 'kawf_no', 'mobile_number', 'due_amount')
    search_fields = ('user__first_name', 'user__last_name', 'enrolment_no', 'kawf_no')
    list_filter = ('blood_group', 'date_of_enrolment', 'joined_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('advocate', 'serial_number', 'amount', 'month', 'year', 'payment_date')
    search_fields = ('serial_number', 'advocate__enrolment_no',)
    list_filter = ('month', 'year')

@admin.register(MonthlyPaymentDue)
class MonthlyPaymentDueAdmin(admin.ModelAdmin):
    list_display = ('advocate', 'month', 'year', 'amount', 'paid')
    search_fields = ('advocate__enrolment_no',)
    list_filter = ('month', 'year', 'paid')
