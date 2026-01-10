# ConstructEYE

A construction site monitoring system built with Django that provides real-time surveillance, safety violation detection, and progress tracking.

## Features

- **Project Management** - Track construction projects with design document storage
- **Camera Surveillance** - Integrate cameras for real-time site monitoring
- **Safety Violation Detection** - Automatic detection and alerting for safety violations (e.g., missing hard hats)
- **Injury Alerts** - Immediate alerts when injuries are detected
- **Inactivity Monitoring** - Detect and report site inactivity
- **Daily Progress Tracking** - Monitor construction progress with percentage updates
- **Report Generation** - Generate progress and safety reports

## Tech Stack

- Python 3.13+
- Django 6.0
- MySQL
- Pipenv

## Prerequisites

- Python 3.13 or higher
- MySQL database server
- Pipenv

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/construct_EYE.git
   cd construct_EYE
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root with the following variables:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=True
   DATABASE_URL=mysql://user:password@localhost:3306/construct_eye
   ```

4. **Set up MySQL database**
   
   Make sure MySQL server is running, then create the database:
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE construct_eye;
   EXIT;
   ```
   
   Update your `.env` file with the root credentials:
   ```env
   DATABASE_URL=mysql://root:your_password@localhost:3306/construct_eye
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```


6. **Run the development server**
   ```bash
   python manage.py runserver
   ```


## Project Structure

```
construct_EYE/
├── backend/              # Main application
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── urls.py           # URL routing
│   └── migrations/       # Database migrations
├── config/               # Django project configuration
│   ├── settings.py       # Project settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI entry point
├── manage.py             # Django management script
├── Pipfile               # Dependencies
└── .env                  # Environment variables (not in repo)
```

## User Roles

| Role | Description |
|------|-------------|
| **Administrator** | Full system access and management |
| **Engineer** | Supervising engineer with project monitoring access |
| **Owner** | Property owner with view access to their projects |

## Models

- **Project** - Construction projects with location and design images
- **User** - Custom user model with role-based access
- **ProjectMember** - Many-to-many relationship between users and projects
- **Camera** - Surveillance cameras linked to projects
- **SafetyViolation** - Detected safety violations with evidence
- **InjuryAlert** - Injury detection alerts
- **InactivityAlert** - Site inactivity alerts
- **DailyProgressUpdate** - Daily progress tracking
- **Report** - Generated project reports

## License

MIT
