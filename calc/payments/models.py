from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from datetime import date


class Advocate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advocate', null=True, blank=True)
    
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5)
    enrolment_no = models.CharField(max_length=20, unique=True)
    date_of_enrolment = models.DateField()
    bar_registration = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    joined_date = models.DateField()
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    
    picture = models.ImageField(upload_to='media/advocate_pictures/', blank=True)

    def __str__(self):
        return self.user.get_full_name() if self.user else f"Advocate {self.enrolment_no}"

    def calculate_due(self):
        """Calculate total due amount for the advocate from January to the current month."""
        year = now().year
        current_month = now().month
        due_amount = 0

        # Check payments made
        paid_months = Payment.objects.filter(advocate=self, start_month__year=year).values_list('start_month__month', flat=True)

        # Calculate dues for missed months
        for month in range(1, current_month + 1):  # From Jan to current month
            if month not in paid_months:
                due_amount += 100
                if month == 9:  # September extra ₹500
                    due_amount += 500

        return due_amount

class Payment(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_month = models.DateField()  # The month this payment covers
    end_month = models.DateField()    # Can be same as start_month or a later month
    payment_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=[('Completed', 'Completed'), ('Pending', 'Pending')], default='Completed')

    def __str__(self):
        return f"{self.advocate.user.get_full_name()} - ₹{self.amount} on {self.payment_date}"

class MonthlyPaymentDue(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, related_name='monthly_dues')
    month = models.DateField()  # The month this due is for
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    def __str__(self):
        return f"{self.advocate.name} - ₹{self.amount_due} due for {self.month.strftime('%B %Y')}"