# CALC (Counsel Accounting and Ledger Control)

**CALC** is a Django-based web application developed for the Hosdurg Bar Association. It aims to manage advocate details and track their monthly payments to the association. The project helps in maintaining an organized accounting system and provides features for payment tracking and reminders.

## Features

- **Advocate Management:** Store and manage details of advocates, including registration number, contact information, and address.
- **Payment Tracking:** Record payments made by advocates, including support for paying multiple months at once.
- **Monthly Dues Management:** Automatically track monthly dues for each advocate, and mark payments as completed.
- **Automated Reminders:** Send notifications to advocates for overdue payments.
- **Admin Dashboard:** Provide an interface for administrators to manage advocates and monitor payments.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/CALC.git
   cd CALC
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the Django project:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. **Access the application:**
   - Open `http://127.0.0.1:8000/` in your web browser.

## Project Structure

- `calc_project/` – Main project folder containing settings and configurations.
- `accounting/` – App for managing advocate details and payment tracking.
- `templates/` – HTML templates for the web interface.
- `static/` – Static files (CSS, JavaScript, images).

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- Developed by Abhinav Raj for the Hosdurg Bar Association.
- Special thanks to the members of the association for their support and feedback.