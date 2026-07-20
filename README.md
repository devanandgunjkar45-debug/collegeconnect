# CampusConnect

CampusConnect is a modern campus event management platform built with Django, Bootstrap, and rich student/administrator workflows. It helps colleges manage events, announcements, registrations, attendance, certificates, and campus communities from one polished portal.

## Key Features
- Role-based access: Admin, Student, Coordinator, Organizer
- Event discovery, approval workflows, and registration tracking
- QR pass generation and attendance verification
- Notifications, announcements, and event galleries
- Responsive UI with dark/light mode and polished landing pages
- Secure e-mail settings, deployment-ready static/media configuration

## Technology Stack
- Python 3.x
- Django 4.x
- Bootstrap 5
- SQLite / MySQL
- qrcode, Pillow, reportlab

## Local Setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with production-ready variables.
4. Apply migrations:
```bash
python manage.py migrate
```
5. Create a superuser:
```bash
python manage.py createsuperuser
```
6. Start the development server:
```bash
python manage.py runserver
```

## Environment Variables
Use `.env` for environment-specific configuration. Example values are available in `sample_env.txt`.

Required settings:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Optional local settings:
- `DJANGO_ALLOWED_HOSTS` (set `127.0.0.1 localhost` for local development)

If you want to host on PythonAnywhere, set `DJANGO_DEBUG=False`, add your PythonAnywhere domain to `DJANGO_ALLOWED_HOSTS`, and configure the app using PythonAnywhere's web app settings.

PythonAnywhere deployment steps:
1. Create a new PythonAnywhere web app and choose the same Python version as your project.
2. Upload the project files with the Files tab, or open a Bash console and run:
   ```bash
   git clone <your-repo-url> ~/project
   cd ~/project
   ```
3. Create and activate a virtualenv in PythonAnywhere:
   ```bash
   python3.12 -m venv ~/venv/campusconnect
   source ~/venv/campusconnect/bin/activate
   pip install -r ~/project/requirements.txt
   ```
4. In the PythonAnywhere Web tab, add these environment variables:
   - `DJANGO_SECRET_KEY=<your-secret-key>`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<your-username>.pythonanywhere.com`
   - any email or database variables your app requires
5. In the Web tab, set the Working directory to `/home/<your-username>/project` and edit the WSGI file:
   ```python
   import os
   import sys

   path = '/home/<your-username>/project'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'campusconnect.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
6. In a Bash console, run:
   ```bash
   cd ~/project
   source ~/venv/campusconnect/bin/activate
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
7. Reload your web app from the PythonAnywhere Web tab.

Optional production settings:
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SECURE_HSTS_SECONDS`
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `DJANGO_SECURE_HSTS_PRELOAD`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_USE_WHITENOISE`
- `DB_ENGINE`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`

## Production Deployment Guide
1. Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS`.
2. Configure a production database (MySQL or PostgreSQL).
3. Run `python manage.py collectstatic`.
4. Set up a web server such as Gunicorn + Nginx or any PaaS provider.
5. Make sure `STATIC_ROOT` and `MEDIA_ROOT` are served correctly.
6. Use HTTPS and turn on security headers via environment variables.

## Docker Deployment
The project includes a `Dockerfile`, `docker-compose.yml`, and `.dockerignore`.

1. Build the Docker image:
```bash
docker build -t campusconnect:latest .
```
2. Start containers:
```bash
docker compose up -d
```
3. Run migrations inside the web container:
```bash
docker compose exec web python manage.py migrate
```
4. Create a superuser:
```bash
docker compose exec web python manage.py createsuperuser
```
5. Collect static files:
```bash
docker compose exec web python manage.py collectstatic --noinput
```

If you use MySQL with Docker Compose, the database service is configured in `docker-compose.yml`.

## Deployment Checklist
- [x] Secret key stored in environment variables
- [x] Debug mode disabled for production
- [x] Allowed hosts configured
- [x] Static files collected via `collectstatic`
- [x] Media files stored in `MEDIA_ROOT`
- [x] Email backend configured for real notifications
- [x] HTTPS/SSL redirect enabled for production
- [x] CSRF trusted origins configured if using a custom domain

## Recommended Improvements
- Add password reset and email verification flows
- Add admin analytics dashboards and usage reports
- Add automated tests for user roles, registration, and event approval
- Add CI/CD deployment pipeline to keep production updated
