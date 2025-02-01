from django.db import models
from django.contrib.auth.models import User

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
    
    picture = models.ImageField(upload_to='static/images/user', blank=True)

    def __str__(self):
        return self.user.get_full_name()  # Access the full name via the User model

class Payment(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    months_paid_for = models.IntegerField()  # Store months paid in a format like 3 for Jan-Mar
    start_month = models.DateField()
    end_month = models.DateField()
    status = models.CharField(max_length=50, default="Pending")
    receipt_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.advocate.name} - {self.payment_date}"

class MonthlyPaymentDue(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    due_month = models.DateField()  # Each due month for the advocate
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.advocate.name} - {self.due_month}"
