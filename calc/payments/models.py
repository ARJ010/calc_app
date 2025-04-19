from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.utils import timezone

# --- Choices for month ---
MONTH_CHOICES = [
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]

class Advocate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advocate', null=True, blank=True)
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5)
    enrolment_no = models.CharField(max_length=20, unique=True)
    kawf_no = models.CharField(max_length=20, unique=True,blank=True,null=True)
    date_of_enrolment = models.DateField()
    bar_registration = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    joined_date = models.DateField()
    due_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # ₹ value

    
    picture = models.ImageField(upload_to='media/advocate_pictures/', blank=True)

    def __str__(self):
        return self.user.get_full_name() if self.user else f"Advocate {self.enrolment_no}"


class Payment(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)
    year = models.IntegerField()
    payment_date = models.DateField(default=timezone.now)
    serial_number = models.CharField(max_length=50)  # format: MM-YYYY.1 or MM-YYYY.debt

    def __str__(self):
        return f"{self.advocate.user.first_name} - ₹{self.amount} for {self.month}/{self.year}"


class MonthlyPaymentDue(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)  # Newly added field

    class Meta:
        unique_together = ('advocate', 'month', 'year')
        ordering = ['year', 'month']

    def __str__(self):
        return f"DUE: {self.advocate.user.first_name} - ₹{self.amount} for {self.month}/{self.year}"
