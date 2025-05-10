import csv
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import CSVUploadForm,UserForm,AdvocateForm,EditUserForm, CustomUserChangeForm
from .models import Payment, Advocate, MonthlyPaymentDue
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.db.models import Q
from decimal import Decimal  
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test

# Ensure only superusers or users with the "Admin" group can access
def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_superuser


def manage_admins(request):
    users = User.objects.exclude(username=request.user.username)  # Exclude logged-in user
    admin_group = Group.objects.get(name='Admin')  # Get the "Admin" group

    # Get all users who are part of the Admin group
    admin_users = admin_group.user_set.all()

    # Fetch advocates (excluding logged-in user)
    advocates = Advocate.objects.exclude(user=request.user)  # Exclude logged-in user

    if request.method == 'POST':
        if 'add_admin' in request.POST:
            username = request.POST.get('username')
            user = User.objects.filter(username=username).first()
            if user and user != request.user:  # Ensure the logged-in user is not added as admin
                # Add the user to the "Admin" group
                admin_group.user_set.add(user)
                messages.success(request, f'{user.username} has been added to the Admin group.')
            else:
                messages.error(request, 'Invalid user or you cannot add yourself.')

        elif 'remove_admin' in request.POST:
            username = request.POST.get('username')
            user = User.objects.filter(username=username).first()
            
            # Ensure the logged-in user is not trying to remove themselves
            if user == request.user:
                messages.error(request, 'You cannot remove yourself from the Admin group.')
                return redirect('manage_admins')

            # Check if the admin user has an associated advocate
            try:
                advocate = user.advocate
            except Advocate.DoesNotExist:
                advocate = None

            # Only allow removal of an admin if they have an associated Advocate object
            if advocate:
                # Remove the user from the "Admin" group
                admin_group.user_set.remove(user)
                messages.success(request, f'{user.username} has been removed from the Admin group.')
            else:
                # Admins without an Advocate object cannot be removed, but can still be edited
                messages.error(request, 'This admin cannot be removed as they do not have an associated Advocate object.')

    return render(request, 'payments/manage_admins.html', {
        'users': users,
        'admin_users': admin_users,
        'advocates': advocates
    })

from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect

# Edit Admin View
# Edit Admin View
def edit_admin(request):
    user = request.user

    # Ensure the user is an admin
    if not user.groups.filter(name='Admin').exists():
        messages.error(request, "You do not have permission to edit this page.")
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)

        if form.is_valid():
            # Check if password is provided and set it
            new_password = form.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)  # Set new password if provided
            form.save()  # Save the other fields (first name, last name, email, etc.)

            user.save()  # Save the user instance with updated details
            messages.success(request, "Admin details updated successfully!")
            return redirect('index')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'payments/edit_admin.html', {'form': form})



# Create your views here.


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Advocate


@login_required
def index(request):
    is_admin = request.user.groups.filter(name='Admin').exists()

    try:
        advocate = Advocate.objects.get(user=request.user)
        due_entries = MonthlyPaymentDue.objects.filter(advocate=advocate, paid=False).order_by('year', 'month')
        recent_payments = Payment.objects.filter(advocate=advocate).order_by('-payment_date')[:10]
    except Advocate.DoesNotExist:
        advocate = None
        due_entries = None
        recent_payments = None
        if not is_admin:
            # Create only for non-admins
            advocate = Advocate.objects.create(
                user=request.user,
                enrolment_no="DUMMY1234",
                mobile_number="0000000000",
                address="Dummy Address"
            )

    return render(request, 'payments/index.html', {
        'advocate': advocate,
        'is_admin': is_admin,
        'due_entries': due_entries,
        'recent_payments': recent_payments
    })


from django.shortcuts import render
from .models import Advocate, Payment, MonthlyPaymentDue
from django.db.models import Q

from .models import Advocate, Payment, MonthlyPaymentDue, MONTH_CHOICES

def payment_due_report(request):
    advocates = Advocate.objects.all()
    selected_advocate = request.GET.get('advocate')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    status = request.GET.get('status')  # "paid", "unpaid", "all"

    payments = Payment.objects.all()
    dues = MonthlyPaymentDue.objects.all()

    if selected_advocate:
        payments = payments.filter(advocate__id=selected_advocate)
        dues = dues.filter(advocate__id=selected_advocate)

    if selected_month:
        payments = payments.filter(month=selected_month)
        dues = dues.filter(month=selected_month)

    if selected_year:
        payments = payments.filter(year=selected_year)
        dues = dues.filter(year=selected_year)

    if status == 'paid':
        dues = dues.filter(paid=True)
    elif status == 'unpaid':
        dues = dues.filter(paid=False)

    context = {
        'advocates': advocates,
        'payments': payments,
        'dues': dues,
        'filters': {
            'advocate': selected_advocate,
            'month': selected_month,
            'year': selected_year,
            'status': status
        },
        'MONTH_CHOICES': MONTH_CHOICES,  # 👈 Add this line
    }
    return render(request, 'payments/report.html', context)





def advocate_list(request):
    search_query = request.GET.get('search', '')  # Get search query from the GET request

    if search_query:
        # Search by first name, last name, or enrolment number
        advocates = Advocate.objects.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(enrolment_no__icontains=search_query)
        )
    else:
        advocates = Advocate.objects.all()

    return render(request, 'payments/advocate_list.html', {'advocates': advocates, 'search_query': search_query})



def register_advocate(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        advocate_form = AdvocateForm(request.POST, request.FILES)

        if user_form.is_valid() and advocate_form.is_valid():
            try:
                with transaction.atomic():
                    # Save the User instance
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()

                    # Save the Advocate instance
                    advocate = advocate_form.save(commit=False)
                    advocate.user = user
                    advocate.save()

                messages.success(request, "Advocate registered successfully.")
                return redirect('advocate_list')
            except Exception as e:
                messages.error(request, f"Error: {e}")
                return redirect('register_advocate')

    else:
        user_form = UserForm()
        advocate_form = AdvocateForm()

    return render(request, 'payments/register.html', {
        'user_form': user_form,
        'advocate_form': advocate_form,
    })



# Edit Advocate Profile

def edit_advocate(request, advocate_id):
    advocate = get_object_or_404(Advocate, id=advocate_id)
    user = advocate.user  # Get the associated User instance

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        advocate_form = AdvocateForm(request.POST, request.FILES, instance=advocate)

        if user_form.is_valid() and advocate_form.is_valid():
            user_form.save()
            advocate_form.save()
            messages.success(request, "Advocate's profile has been updated successfully.")
            return redirect('advocate_list')  # Redirect to the advocate list after editing
        else:
            # You may want to show form errors here
            print(user_form.errors)
            print(advocate_form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = EditUserForm(instance=user)
        advocate_form = AdvocateForm(instance=advocate)

    return render(request, 'payments/edit_advocate.html', {
        'user_form': user_form,
        'advocate_form': advocate_form,
    })


def advocate_detail(request, advocate_id):
    advocate = get_object_or_404(Advocate, id=advocate_id)
    name = advocate.user.first_name + " " + advocate.user.last_name

    due_entries = MonthlyPaymentDue.objects.filter(advocate=advocate, paid=False).order_by('year', 'month')
    recent_payments = Payment.objects.filter(advocate=advocate).order_by('-payment_date')[:10]

    return render(request, 'payments/advocate_details.html', {
        'advocate': advocate,
        'name':name,
        'due_entries': due_entries,
        'recent_payments': recent_payments
    })



# For handling due_amount safely

def upload_advocates(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                name = row.get('name')
                mobile_number = row.get('mobile_number')
                date_of_birth = row.get('date_of_birth')
                blood_group = row.get('blood_group')
                enrolment_no = row.get('enrolment_no')
                kawf_no = row.get('kawf_no')  # New field
                date_of_enrolment = row.get('date_of_enrolment')
                email = row.get('email') or f'{name.split()[0].lower()}@example.com'
                address = row.get('address')
                joined_date = row.get('joined_date')
                picture = row.get('picture')
                due_amount_str = row.get('due_amount', '0.00')  # Default to 0.00 if missing

                try:
                    due_amount = Decimal(due_amount_str) if due_amount_str else Decimal('0.00')
                except:
                    due_amount = Decimal('0.00')

                try:
                    if Advocate.objects.filter(enrolment_no=enrolment_no).exists():
                        messages.warning(request, f"Advocate with enrolment number '{enrolment_no}' already exists. Skipping.")
                        continue
                    
                    password = f'pass@123'
                    user = User.objects.create_user(username=mobile_number, email=email, password=password)
                    user.first_name = name.split()[0]
                    user.last_name = name.split()[1] if len(name.split()) > 1 else ''
                    user.save()

                    with transaction.atomic():
                        advocate = Advocate.objects.create(
                            user=user,
                            mobile_number=mobile_number,
                            date_of_birth=date_of_birth,
                            blood_group=blood_group,
                            enrolment_no=enrolment_no,
                            kawf_no=kawf_no,  # Include kawf_no
                            date_of_enrolment=date_of_enrolment,
                            email=email,
                            address=address,
                            joined_date=joined_date,
                            due_amount=due_amount,  # Include due_amount
                            picture=picture,
                        )
                    messages.success(request, f"Advocate '{name}' uploaded successfully!")

                except Exception as e:
                    messages.error(request, f"Error uploading advocate '{name}': {e}")
                    continue

            return redirect('advocate_list')

    else:
        form = CSVUploadForm()

    return render(request, 'payments/bulk_register.html', {'form': form})



def download_advocate_template(request):
    # Create the HTTP response with the appropriate content type for a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="advocate_template.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row (field names)
    writer.writerow([
        'name', 'mobile_number', 'date_of_birth', 'blood_group', 'enrolment_no',
        'date_of_enrolment', 'kawf_no', 'email', 'address',
        'joined_date', 'due_amount'
    ])

    # Write two dummy rows
    writer.writerow([
        'John Doe', '234567819', '1990-01-01', 'O+', 'KL12345',
        '2015-06-15', 'KAWF001', 'john@example.com',
        '123 Advocate Street, Cityville', '2020-01-01', '0.00'
    ])
    writer.writerow([
        'Jane Smith', '123456789', '1988-12-05', 'A-', 'KL67890',
        '2017-03-20', 'KAWF002', 'jane@example.com',
        '456 Legal Lane, Lawtown', '2021-05-10', '0.00'
    ])

    return response







def export_advocates_csv(request):
    # Create the HttpResponse object with the content-type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="advocates_list.csv"'
    
    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Name', 'Mobile Number', 'Date of Birth', 'Blood Group', 'Enrolment No', 
                     'Date of Enrolment', 'Email', 'Address', 'Joined Date'])
    
    # Query all advocates and write to CSV
    advocates = Advocate.objects.all()
    for advocate in advocates:
        writer.writerow([advocate.user.first_name+" "+advocate.user.last_name, advocate.mobile_number, advocate.date_of_birth, advocate.blood_group, 
                         advocate.enrolment_no, advocate.date_of_enrolment, advocate.email,
                         advocate.address, advocate.joined_date])
    
    return response



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Advocate, MonthlyPaymentDue, Payment
from datetime import datetime, timedelta
from calendar import monthrange
from django.db import IntegrityError


def check_and_update_dues(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Only allow checking and updating dues if the current year is 2025 and the current date is April or later
    if current_year == 2025:
        # Format current_month as a 2-digit string
        current_month_str = f"{current_month:02d}"

        # Check if dues have already been checked for the current month and year
        if MonthlyPaymentDue.objects.filter(year=current_year, month=current_month_str).exists():
            messages.warning(request, "The monthly dues have already been checked for this month.")
            return redirect('advocate_list')  # Redirect to a page listing all advocates

        # Loop through the months from April to the current month and year
        for month in range(5, current_month + 1):  # Start from May (month 5)
            month_str = f"{month:02d}"

            # Check for advocates who have not paid for this month and create MonthlyPaymentDue entries
            advocates = Advocate.objects.all()
            for advocate in advocates:
                total_paid = Payment.objects.filter(advocate=advocate, year=current_year, month=month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                
                if total_paid < Decimal('100.00'):  # Example, assuming ₹100 is the required monthly payment
                    if not MonthlyPaymentDue.objects.filter(advocate=advocate, month=month_str, year=current_year).exists():
                        try:
                            amount_due = Decimal('100.00')
                            if month == 9:  # If the month is September, charge ₹600
                                amount_due = Decimal('600.00')

                            MonthlyPaymentDue.objects.create(
                                advocate=advocate,
                                month=month_str,
                                year=current_year,
                                amount=amount_due,
                                paid=False
                            )

                            # Only update due_amount if the advocate was added to MonthlyPaymentDue
                            advocate.due_amount += amount_due
                            advocate.save()

                        except IntegrityError:
                            messages.error(request, f"Error: Could not create due entry for {advocate.user.first_name}.")

        messages.success(request, f"Monthly dues for {current_month_str}/{current_year} have been checked and updated successfully.")
        return redirect('payment_due_report')  # Redirect to a page listing all advocates

    # Format current_month as a 2-digit string
    current_month_str = f"{current_month:02d}"

    # Check if dues have already been checked for the current month and year
    if MonthlyPaymentDue.objects.filter(year=current_year, month=current_month_str).exists():
        messages.warning(request, "The monthly dues have already been checked for this month.")
        return redirect('payment_due_report')  # Redirect to a page listing all advocates

    # Loop through the months from April to the current month and year
    for month in range(1, current_month + 1):  # Start from April (month 4)
        month_str = f"{month:02d}"

        # Check for advocates who have not paid for this month and create MonthlyPaymentDue entries
        advocates = Advocate.objects.all()
        for advocate in advocates:
            total_paid = Payment.objects.filter(advocate=advocate, year=current_year, month=month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            if total_paid < Decimal('100.00'):  # Example, assuming ₹100 is the required monthly payment
                if not MonthlyPaymentDue.objects.filter(advocate=advocate, month=month_str, year=current_year).exists():
                    try:
                        amount_due = Decimal('100.00')
                        if month == 9:  # If the month is September, charge ₹600
                            amount_due = Decimal('600.00')

                        MonthlyPaymentDue.objects.create(
                            advocate=advocate,
                            month=month_str,
                            year=current_year,
                            amount=amount_due,
                            paid=False
                        )

                        # Only update due_amount if the advocate was added to MonthlyPaymentDue
                        advocate.due_amount += amount_due
                        advocate.save()

                    except IntegrityError:
                        messages.error(request, f"Error: Could not create due entry for {advocate.user.first_name}.")

    messages.success(request, f"Monthly dues for {current_month_str}/{current_year} have been checked and updated successfully.")
    return redirect('payment_due_report')  # Redirect to a page listing all advocates

from decimal import Decimal
from django.db.models import Sum


def debt_pay(request, advocate_id):
    advocate = get_object_or_404(Advocate, id=advocate_id)
    name = advocate.user.first_name + " " + advocate.user.last_name
    unpaid_dues = MonthlyPaymentDue.objects.filter(advocate=advocate, paid=False).order_by('year', 'month')

    # Calculate the total unpaid dues
    total_unpaid_dues = unpaid_dues.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    show_extra_due = advocate.due_amount > total_unpaid_dues

    if request.method == 'POST':
        selected_due_ids = request.POST.getlist('due_ids')
        extra_due_amount = request.POST.get('extra_due', '0').strip()
        total_paid = Decimal('0.00')

        # Handle selected MonthlyPaymentDue entries
        for due_id in selected_due_ids:
            due_entry = MonthlyPaymentDue.objects.filter(id=due_id, advocate=advocate, paid=False).first()
            if due_entry:
                month_str = f"{int(due_entry.month):02d}"
                serial = f"{month_str}-{due_entry.year}.debt"
                
                Payment.objects.create(
                    advocate=advocate,
                    amount=due_entry.amount,
                    month=month_str,
                    year=due_entry.year,
                    serial_number=serial
                )

                due_entry.paid = True
                due_entry.save()

                total_paid += due_entry.amount

                # Reduce the due_amount in the advocate's profile
                advocate.due_amount -= due_entry.amount
                advocate.save()

        # Handle partial due_amount payment
        try:
            extra_amount = Decimal(extra_due_amount)
        except:
            extra_amount = Decimal('0.00')

        if extra_amount > 0 and advocate.due_amount > 0:
            actual_deducted = min(extra_amount, advocate.due_amount)
            today = timezone.now()
            month_str = f"{today.month:02d}"
            year = today.year
            serial = f"{month_str}-{year}.debt-extra"

            Payment.objects.create(
                advocate=advocate,
                amount=actual_deducted,
                month=month_str,
                year=year,
                serial_number=serial
            )

            advocate.due_amount -= actual_deducted
            advocate.save()

            total_paid += actual_deducted

        if total_paid > 0:
            messages.success(request, f"Successfully paid ₹{total_paid} for {advocate.user.first_name}.")
        else:
            messages.warning(request, "No dues selected or amount entered.")

        return redirect('advocate_details', advocate_id=advocate.id)

    return render(request, 'payments/debt_pay.html', {
        'advocate': advocate,
        'name':name,
        'unpaid_dues': unpaid_dues,
        'show_extra_due': show_extra_due  # Pass the flag to the template
    })




from django.shortcuts import render, get_object_or_404, redirect
from .models import Advocate, Payment
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import calendar

# View for Normal Pay with start and end month/year
def normal_pay(request, advocate_id):
    advocate = get_object_or_404(Advocate, id=advocate_id)
    name = advocate.user.first_name + " " + advocate.user.last_name

    # Get current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # List of months for the dropdown menu
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    if request.method == "POST":
        start_month = int(request.POST['start_month'])
        start_year = int(request.POST['start_year'])
        end_month = int(request.POST['end_month'])
        end_year = int(request.POST['end_year'])

        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)

        # Ensure the end date is not before the start date
        if start_date > end_date:
            messages.error(request, "End date cannot be before the start date.")
            return redirect('normal_pay', advocate_id=advocate.id)

        # Ensure that the end date is not before the current date
        current_date = datetime(current_year, current_month, 1)
        if end_date < current_date:
            messages.error(request, "End date cannot be earlier than the current month.")
            return redirect('normal_pay', advocate_id=advocate.id)

        # Ensure no duplicate month-year pairs
        existing_payments = Payment.objects.filter(advocate=advocate)
        existing_payment_month_years = {(payment.month, payment.year) for payment in existing_payments}
        existing_due_month_years = {
            (due.month, due.year) for due in MonthlyPaymentDue.objects.filter(advocate=advocate, paid=False)
        }

        # Combine both sets
        existing_month_years = existing_payment_month_years.union(existing_due_month_years)

        # Start adding payments month by month
        current_date = start_date
        serial_number_counter = 1  # Initialize the counter for serial numbers

        while current_date <= end_date:
            month_str = current_date.strftime('%m')  # Format the month to MM
            year_str = current_date.year

            # Check if the month-year pair already exists
            if (month_str, year_str) in existing_payment_month_years:
                messages.error(request, f"Payment for {calendar.month_name[current_date.month]} {current_date.year} already exists.")
                return redirect('normal_pay', advocate_id=advocate.id)
            elif (month_str, year_str) in existing_due_month_years:
                messages.error(request, f"Due for {calendar.month_name[current_date.month]} {current_date.year} already exists.")
                return redirect('normal_pay', advocate_id=advocate.id)


            # Create a unique serial number, e.g., 'MM-YYYY.1'
            serial_number = f"{month_str}-{year_str}.{serial_number_counter}"

            # Create and save the payment
            payment = Payment(
                advocate=advocate,
                amount=100.00,  # ₹100 per month (change as needed)
                month=month_str,
                year=year_str,
                serial_number=serial_number,
                payment_date=timezone.now()
            )
            payment.save()

            # Increment serial number and move to the next month
            serial_number_counter += 1
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)

        messages.success(request, "Payments created successfully for the selected months.")
        return redirect('advocate_details', advocate_id=advocate.id)

    return render(request, 'payments/normal_pay.html', {
        'advocate': advocate, 
        'name':name,
        'months': months,
        'current_year': current_year, 
        'current_month': current_month
    })



from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib import messages
from .forms import ChangeUsernamePasswordForm

def change_username_password(request):
    if request.method == 'POST':
        form = ChangeUsernamePasswordForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_password = form.cleaned_data['password']
            
            try:
                # Change the username
                user = request.user
                user.username = new_username
                user.set_password(new_password)
                user.save()

                # Update the session to avoid logout after password change
                update_session_auth_hash(request, user)

                # Log out the user after the changes
                logout(request)

                # Display a success message and redirect to login page
                messages.success(request, "Your username and password have been updated. Please log in again.")
                return redirect('login')  # Redirect to the login page

            except Exception as e:
                messages.error(request, f"Error updating username/password : Username already exists")
                return redirect('change_username_password')

    else:
        form = ChangeUsernamePasswordForm()

    return render(request, 'payments/change_username_password.html', {'form': form})



def reset_advocate_credentials(request, advocate_id):
    try:
        # Get the Advocate object based on advocate_id
        advocate = get_object_or_404(Advocate, id=advocate_id)
        
        # Find the associated User object
        user = advocate.user

        # Reset username to a unique detail (e.g., enrolment number)
        user.username = advocate.mobile_number  # Or any other unique detail
        user.set_password('pass@123')  # Common password
        user.save()

        # Keep the user session active after password change
        update_session_auth_hash(request, user)

        messages.success(request, f"Username and password reset for Advocate {advocate.user.first_name} with username:{advocate.mobile_number} and password:pass@123.")
        return redirect('advocate_details', advocate_id=advocate.id)  # Or wherever you want to redirect

    except Advocate.DoesNotExist:
        messages.error(request, f"Advocate with ID {advocate_id} does not exist.")
        return redirect(reverse('reset_advocate_credentials', args=[advocate_id]))

    except Exception as e:
        messages.error(request, f"Error resetting credentials: {e}")
        return redirect(reverse('reset_advocate_credentials', args=[advocate_id]))
    
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Advocate
from django.contrib.auth.models import User

def delete_advocate(request, advocate_id):
    # Get the advocate object
    advocate = get_object_or_404(Advocate, id=advocate_id)

    # Check if the current user is trying to delete themselves
    if advocate.user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('advocate_list')  # Redirect to the advocate listing page

    # Check if the user is in the "Admin" group
    if request.user.groups.filter(name='Admin').exists():
        # Get the associated user
        user = advocate.user
        
        # Delete the advocate and the associated user
        advocate.delete()  # This deletes the advocate instance
        if user:
            user.delete()  # This deletes the associated user
        
        messages.success(request, 'Advocate and their account were successfully deleted.')
    else:
        messages.error(request, 'You do not have permission to delete this advocate.')

    return redirect('advocate_list')  # Redirect back to the advocate listing page


from django.http import HttpResponseNotFound

def handle_unknown_path(request, unknown_path):
    return HttpResponseNotFound('Page not found.')


from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile

def generate_experience_certificate(request, advocate_id):
    advocate = Advocate.objects.get(id=advocate_id)

    # Render the HTML string with advocate details
    html_string = render_to_string('payments/certificate_template.html', {
        'advocate_name': advocate.user.get_full_name(),
        'enrolment_date': advocate.date_of_enrolment.strftime('%d-%m-%Y'),
        'roll_no': advocate.enrolment_no,
        'joined_date': advocate.joined_date.strftime('%d-%m-%Y'),
    })

    # Generate PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Experience_Certificate_{advocate.user.get_full_name()}.pdf'

    # Generate PDF from the HTML string with A4 size
    HTML(string=html_string).write_pdf(target=response, stylesheets=[CSS(string='@page { size: A4; margin: 0; }')])

    return response
