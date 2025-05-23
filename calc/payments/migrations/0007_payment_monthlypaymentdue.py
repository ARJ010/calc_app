# Generated by Django 4.2.7 on 2025-02-01 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_remove_payment_advocate_alter_advocate_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('months_paid_for', models.IntegerField()),
                ('start_month', models.DateField()),
                ('end_month', models.DateField()),
                ('status', models.CharField(default='Pending', max_length=50)),
                ('receipt_number', models.CharField(blank=True, max_length=50, null=True)),
                ('advocate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.advocate')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyPaymentDue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_month', models.DateField()),
                ('is_paid', models.BooleanField(default=False)),
                ('advocate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.advocate')),
            ],
        ),
    ]
