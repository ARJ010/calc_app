import csv
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import CSVUploadForm,UserForm,AdvocateForm,EditUserForm
from .models import Payment, Advocate, MonthlyPaymentDue
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime



# Create your views here.


@login_required()
def index(request):
    advocate = Advocate.objects.get(user=request.user)
    return render(request, 'payments/index.html', {'advocate': advocate})


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
                return redirect('advocate_list')  # Redirect to a success URL (you can change this)
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
        user_form = EditUserForm(instance=user)
        advocate_form = AdvocateForm(instance=advocate)

    return render(request, 'payments/edit_advocate.html', {
        'user_form': user_form,
        'advocate_form': advocate_form,
    })


def advocate_detail(request, advocate_id):
    # Fetch the advocate by primary key (pk) or any other unique identifier
    advocate = get_object_or_404(Advocate, id=advocate_id)
    
    # Render the template and pass the advocate object
    return render(request, 'payments/advocate_details.html', {'advocate': advocate})



def upload_advocates(request):
    if request.method == 'POST' and request.FILES['csv_file']:
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
                date_of_enrolment = row.get('date_of_enrolment')
                bar_registration = row.get('bar_registration')
                email = row.get('email') or f'{name.split()[0].lower()}@example.com'  # Default email if missing
                address = row.get('address')
                joined_date = row.get('joined_date')
                picture = row.get('picture')  # Optional: Handle the picture file upload as needed

                try:
                    # Check if the advocate already exists by enrollment number or bar registration number
                    if Advocate.objects.filter(enrolment_no=enrolment_no).exists():
                        messages.warning(request, f"Advocate with enrolment number '{enrolment_no}' already exists. Skipping.")
                        continue
                    if Advocate.objects.filter(bar_registration=bar_registration).exists():
                        messages.warning(request, f"Advocate with bar registration '{bar_registration}' already exists. Skipping.")
                        continue
                    
                    # Create the User instance
                    username = name.split()[0].lower()  # Username is the first name in lowercase
                    password = f'{username}@123'  # Default password format: first_name@123
                    user = User.objects.create_user(username=bar_registration, email=email, password=password)
                    user.first_name = name.split()[0]
                    user.last_name = name.split()[1] if len(name.split()) > 1 else ''
                    user.save()

                    # Create the Advocate instance and associate it with the user
                    with transaction.atomic():
                        advocate = Advocate.objects.create(
                            user=user,
                            mobile_number=mobile_number,
                            date_of_birth=date_of_birth,
                            blood_group=blood_group,
                            enrolment_no=enrolment_no,
                            date_of_enrolment=date_of_enrolment,
                            bar_registration=bar_registration,
                            email=email,
                            address=address,
                            joined_date=joined_date,
                            picture=picture,  # Handle picture if provided
                        )
                    messages.success(request, f"Advocate '{name}' uploaded successfully!")

                except Exception as e:
                    messages.error(request, f"Error uploading advocate '{name}': {e}")
                    continue

            return redirect('advocate_list')  # Redirect to the advocate list after uploading

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
    writer.writerow(['name', 'mobile_number', 'date_of_birth', 'blood_group', 'enrolment_no', 'date_of_enrolment',
                     'bar_registration', 'email', 'address', 'joined_date', 'picture'])

    # Fetch all the advocate data
    advocates = Advocate.objects.all()

    # Write the advocate data to the CSV file
    for advocate in advocates:
        writer.writerow([advocate.user.get_full_name(), advocate.mobile_number, advocate.date_of_birth, advocate.blood_group,
                         advocate.enrolment_no, advocate.date_of_enrolment, advocate.bar_registration, advocate.email,
                         advocate.address, advocate.joined_date, advocate.picture.url if advocate.picture else ''])

    return response




def export_advocates_csv(request):
    # Create the HttpResponse object with the content-type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="advocates_list.csv"'
    
    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Name', 'Mobile Number', 'Date of Birth', 'Blood Group', 'Enrolment No', 
                     'Date of Enrolment', 'Bar Registration', 'Email', 'Address', 'Joined Date'])
    
    # Query all advocates and write to CSV
    advocates = Advocate.objects.all()
    for advocate in advocates:
        writer.writerow([advocate.user.first_name+" "+advocate.user.last_name, advocate.mobile_number, advocate.date_of_birth, advocate.blood_group, 
                         advocate.enrolment_no, advocate.date_of_enrolment, advocate.bar_registration, advocate.email,
                         advocate.address, advocate.joined_date])
    
    return response



def make_payment(request, advocate_id):
    advocate = Advocate.objects.get(id=advocate_id)
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        months = int(request.POST['months'])
        receipt_number = request.POST['receipt_number']
        payment_date = datetime.now().date()

        # Create a Payment record
        payment = Payment.objects.create(
            advocate=advocate,
            payment_date=payment_date,
            amount=amount,
            months_paid_for=months,
            start_month=payment_date,
            end_month=payment_date,
            status='Paid',
            receipt_number=receipt_number
        )

        # Update MonthlyPaymentDue records
        for month in range(1, months + 1):
            due_month = MonthlyPaymentDue.objects.filter(
                advocate=advocate, due_month__month=month, due_month__year=payment_date.year
            ).first()
            if due_month:
                due_month.is_paid = True
                due_month.save()

        messages.success(request, 'Payment recorded successfully!')
        return redirect('advocate_details', advocate_id=advocate.id)

    return render(request, 'advocate_details.html', {'advocate': advocate})

