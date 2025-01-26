import csv
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import AdvocateCSVUploadForm
from .models import Advocate

# Create your views here.


def index(request):
    return render(request, 'payments/index.html')


def register_user(request):
    if request.method == 'POST':
        # Retrieve data from POST request
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        date_of_birth = request.POST.get('date_of_birth')
        blood_group = request.POST.get('blood_group')
        enrolment_no = request.POST.get('enrolment_no')
        date_of_enrolment = request.POST.get('date_of_enrolment')
        bar_registration = request.POST.get('bar_registration')
        email = request.POST.get('email')
        address = request.POST.get('address')
        joined_date = request.POST.get('joined_date')

        # Validate required fields
        errors = []
        if not name:
            errors.append("Name is required.")
        if not mobile_number:
            errors.append("Mobile number is required.")
        if not email:
            errors.append("Email is required.")
        if not enrolment_no:
            errors.append("Enrolment number is required.")
        if not bar_registration:
            errors.append("Bar registration number is required.")

        # Check for uniqueness of enrolment_no and bar_registration
        if Advocate.objects.filter(enrolment_no=enrolment_no).exists():
            errors.append("This enrolment number is already in use.")
        if Advocate.objects.filter(bar_registration=bar_registration).exists():
            errors.append("This bar registration number is already in use.")

        # If no errors, create the record
        if not errors:
            Advocate.objects.create(
                name=name,
                mobile_number=mobile_number,
                date_of_birth=date_of_birth,
                blood_group=blood_group,
                enrolment_no=enrolment_no,
                date_of_enrolment=date_of_enrolment,
                bar_registration=bar_registration,
                email=email,
                address=address,
                joined_date=joined_date
            )
            return redirect(reverse('advocate_list'))

        # If there are errors, re-render the form with error messages
        return render(request, 'payments/register.html', {
            'errors': errors,
            'form_data': request.POST
        })

    return render(request, 'payments/register.html')


def advocate_list(request):
    # Fetch all advocates from the database
    advocates = Advocate.objects.all()

    # Render the advocates in a template
    return render(request, 'payments/advocate_list.html', {'advocates': advocates})


def advocate_details(request):
    pass

def bulk_register_advocates(request):
    if request.method == 'POST':
        form = AdvocateCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                advocates_to_create = []
                existing_enrolment_numbers = set(Advocate.objects.values_list('enrolment_no', flat=True))

                for row in reader:
                    # Check if enrolment_no already exists
                    if row['enrolment_no'] in existing_enrolment_numbers:
                        messages.error(request, f"Duplicate enrolment number found: {row['enrolment_no']} for advocate {row['name']}. This entry will be skipped.")
                        continue  # Skip this record and move to the next one

                    try:
                        # Add valid advocates to the list
                        advocates_to_create.append(
                            Advocate(
                                name=row['name'],
                                mobile_number=row['mobile_number'],
                                date_of_birth=datetime.strptime(row['date_of_birth'], '%d-%m-%Y').date(),
                                blood_group=row['blood_group'],
                                enrolment_no=row['enrolment_no'],
                                date_of_enrolment=datetime.strptime(row['date_of_enrolment'], '%d-%m-%Y').date(),
                                bar_registration=row['bar_registration'],
                                email=row['email'],
                                address=row['address'],
                                joined_date=datetime.strptime(row['joined_date'], '%d-%m-%Y').date(),
                            )
                        )
                    except ValueError as e:
                        messages.error(request, f"Date format error for row: {row}. Error: {e}")
                        return redirect('bulk_register_advocates')

                # Bulk create advocates
                Advocate.objects.bulk_create(advocates_to_create)
                messages.success(request, "Advocates successfully registered! Duplicates were skipped.")
                return redirect('advocate_list')

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('bulk_register_advocates')

    else:
        form = AdvocateCSVUploadForm()

    return render(request, 'payments/bulk_register.html', {'form': form})