# Shiatsu Booking SaaS

This is a SaaS application for scheduling shiatsu massages. It allows service providers to select available dates and times, while users can log in to book appointments and view available schedules.

## Features

- User registration and login
- Service provider availability management
- Appointment booking
- Display of available schedules

## Project Structure

```
shiatsu-booking-saas/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   ├── bookings/
│   └── availability/
├── templates/
├── static/
├── requirements.txt
├── runtime.txt
└── Procfile
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd shiatsu-booking-saas
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install requirements:**
   ```
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```
   python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```
   python manage.py runserver
   ```

## Deployment

### Using Render

1. Create a new web service on Render.
2. Connect your GitHub repository.
3. Set the build command to `pip install -r requirements.txt` and the start command to `gunicorn config.wsgi`.
4. Configure environment variables for your database and secret key.
5. Deploy the service.

### Using Railway

1. Create a new project on Railway.
2. Connect your GitHub repository.
3. Set up the environment variables.
4. Use the Railway CLI to deploy your application.

### Using PythonAnywhere

1. Sign up for a free account on PythonAnywhere.
2. Create a new web app and select the Django option.
3. Upload your project files.
4. Configure the virtual environment and install requirements.
5. Set up the database and environment variables.
6. Reload your web app to see it live.

## License

This project is licensed under the MIT License.