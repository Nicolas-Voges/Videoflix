# Videoflix Backend

A robust backend API for a video streaming platform built with Django and Django REST Framework. This is a **backend-only project** that provides authentication, video management, and HLS video streaming capabilities.

## Overview

Videoflix Backend is a comprehensive REST API for managing video content and user authentication. It handles user registration, email verification, password management, video uploads, transcoding, and HLS streaming with multiple resolution support.

**Note:** This is a backend project. A separate frontend application is required to interact with this API.

## Prerequisites

- **Docker** and **Docker Compose** (recommended for local development)
- **Python 3.12** (if running without Docker)
- **PostgreSQL** (can be used via Docker)
- **Redis** (required for task queuing)
- **FFmpeg** (required for video transcoding)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Email Templates](#email-templates)

---

## Features

- **User Authentication**
  - User registration with email verification
  - Email-based login with JWT tokens
  - Password reset functionality
  - Token refresh mechanism
  - Token blacklist on logout

- **Video Management**
  - Video upload with metadata (title, description, category, thumbnail)
  - Video status tracking (pending, processing, ready, failed)
  - Automatic video transcoding to multiple resolutions

- **Video Streaming**
  - HLS (HTTP Live Streaming) support
  - Multiple resolution options (120p, 360p, 720p, 1080p)
  - Secure authenticated access to video content

- **Background Processing**
  - Asynchronous video transcoding using Django-RQ
  - Redis-based job queue for reliable task handling

- **Security**
  - JWT-based authentication
  - CORS support for cross-origin requests
  - CSRF protection
  - HttpOnly cookie support for tokens
  - Email-based user verification

## Tech Stack

- **Framework:** Django 5.2.7
- **API:** Django REST Framework 3.16.1
- **Authentication:** djangorestframework-simplejwt 5.5.1
- **Database:** PostgreSQL with psycopg2-binary
- **Task Queue:** Django-RQ with Redis
- **Video Processing:** FFmpeg
- **Email:** Django's built-in email backend
- **Static Files:** WhiteNoise
- **CORS:** django-cors-headers
- **Caching:** django-redis

---

## Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository
2. Create a `.env` file based on `.env.template`:
   ```bash
   cp .env.template .env
   ```
3. Update the `.env` file with your configuration values
4. Build and start the containers:
   ```cmd
   docker compose up --build
   ```

The backend will be available at `http://localhost:8000`

### Option 2: Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv env
   "env\Scripts\activate"  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.template`
5. Set up the database:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Quick Start

### Start the Application

```cmd
docker compose up --build
```

### Run Migrations

```cmd
docker compose exec web python manage.py migrate
```

### Create a Superuser

```cmd
docker compose exec web python manage.py createsuperuser
```

### Access the Admin Panel

Navigate to `http://localhost:8000/admin` and log in with your superuser credentials.

---

## Configuration

### Environment Variables

Copy the `.env.template` file to `.env` and update the values according to your setup:

```bash
cp .env.template .env
```

| Variable | Description |
|----------|-------------|
| `DJANGO_SUPERUSER_USERNAME` | Default superuser username |
| `DJANGO_SUPERUSER_PASSWORD` | Default superuser password |
| `DJANGO_SUPERUSER_EMAIL` | Default superuser email address |
| `SECRET_KEY` | Django secret key for cryptographic operations |
| `DEBUG` | Enable/disable Django debug mode (set to `False` in production) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed host addresses |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins for CSRF protection |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL database user |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_HOST` | PostgreSQL host address |
| `DB_PORT` | PostgreSQL port number |
| `REDIS_HOST` | Redis server hostname |
| `REDIS_LOCATION` | Redis connection URL for caching |
| `REDIS_PORT` | Redis port number |
| `REDIS_DB` | Redis database number |
| `EMAIL_HOST` | SMTP server for sending emails |
| `EMAIL_PORT` | SMTP port (typically 587 or 465) |
| `EMAIL_HOST_USER` | SMTP authentication username |
| `EMAIL_HOST_PASSWORD` | SMTP authentication password |
| `EMAIL_USE_TLS` | Enable TLS encryption for SMTP |
| `EMAIL_USE_SSL` | Enable SSL encryption for SMTP |
| `DEFAULT_FROM_EMAIL` | Sender email address for application emails |
| `USE_EMAIL_FILE_BACKEND` | Set to `True` to save emails locally instead of sending them (DEBUG must be True) |
| `FRONTEND_BASE_URL` | Base URL for frontend application |


---

## Usage

### Access Django Shell

```cmd
docker compose exec web python manage.py shell
```

### Create a User Programmatically

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user(
    username="testuser",
    email="testuser@example.com",
    password="Test123$"
)
```

### Upload and Transcode a Video

1. Use the Django admin panel (`http://localhost:8000/admin`) to upload a video
2. The system automatically queues a transcoding job
3. FFmpeg processes the video into multiple HLS streams
4. Once ready, the video can be streamed at multiple resolutions

### View Background Jobs

```cmd
docker compose exec web python manage.py rqworker default
```

---

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register a new user
- `GET /api/auth/activate/<uidb64>/<token>/` - Activate user account
- `POST /api/auth/login/` - Login and obtain JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/password_reset/` - Request password reset
- `POST /api/auth/password_reset_confirm/<uidb64>/<token>/` - Confirm password reset

### Video Management

- `GET /api/content/video/` - List all available videos
- `GET /api/content/api/video/<movie_id>/<resolution>/index.m3u8` - Get HLS playlist
- `GET /api/content/api/video/<movie_id>/<resolution>/<segment>/` - Get video segment

---

## Project Structure

```
Videoflix/
├── auth_app/                 # Authentication and user management
│   ├── api/
│   │   ├── permissions.py   # JWT authentication classes
│   │   ├── serializers.py   # User serializers
│   │   ├── urls.py          # Auth endpoints
│   │   └── views.py         # Auth views
│   ├── templates/emails/    # Email templates
│   ├── models.py
│   ├── signals.py           # Post-save signals
│   └── utils.py             # Email utilities
│
├── content_app/              # Video management and streaming
│   ├── api/
│   │   ├── serializers.py   # Video serializers
│   │   ├── urls.py          # Video endpoints
│   │   └── views.py         # Video views
│   ├── models.py            # Video model
│   ├── signals.py           # Auto-transcode signal
│   ├── tasks.py             # Background tasks
│   └── utils.py             # FFmpeg utilities
│
├── core/                     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── sent_emails/              # Email log files (for development mode)
│
├── media/                    # User-uploaded videos and media
├── static/                   # Static files
├── backend.Dockerfile       # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── manage.py
├── requirements.txt
└── README.md
```

---

## Email Templates

The application uses HTML email templates for:

- **Account Activation** (`templates/emails/activate_account.html`)
- **Password Reset** (`templates/emails/reset_password.html`)

These templates are rendered with context variables for the user and activation/reset links.

---

## Development Tips
- If your `SECRET_KEY` contains  `$` characters, escape them as `$$` in the `.env` file
- Monitor background jobs: `docker compose logs web`
- Test email functionality: Check `sent_emails/` folder in development mode (requires `USE_EMAIL_FILE_BACKEND` set to `True` in `.env`).
Rename the `.log` file to `.eml` to open it directly in email clients like Outlook to verify email design and formatting.

---

## License

TBD

**Note:** This is a backend-only project. A separate frontend application is required to interact with the API endpoints.
