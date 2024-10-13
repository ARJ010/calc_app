from django.db import models

# Create your models here.

class Advocate(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3)
    enrolment_no = models.CharField(max_length=20, unique=True)
    date_of_enrolment = models.DateField()
    bar_registration = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    address = models.TextField()
    joined_date = models.DateField()

    def __str__(self):
        return self.name

class Payment(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    months_paid_for = models.IntegerField()
    start_month = models.DateField()
    end_month = models.DateField()
    status = models.CharField(max_length=50)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.advocate.name} - {self.payment_date}"

class MonthlyPaymentDue(models.Model):
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    due_month = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.advocate.name} - {self.due_month}"
