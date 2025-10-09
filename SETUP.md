# Nexus Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements/development.txt
```

### 2. Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# At minimum, set SECRET_KEY and DATABASE_URL
```

### 3. Setup Database

```bash
# For SQLite (easiest for development):
# Just set in .env: DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL:
# 1. Install PostgreSQL
# 2. Create database:
createdb nexus

# 3. Set in .env:
# DATABASE_URL=postgres://username:password@localhost:5432/nexus
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

Admin panel: http://localhost:8000/admin

## Optional: Setup Redis and Celery

### Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### Run Celery Worker

```bash
# In a separate terminal
celery -A nexus worker -l info
```

### Run Celery Beat (for scheduled tasks)

```bash
# In another terminal
celery -A nexus beat -l info
```

## Troubleshooting

### Installation Issues

If you encounter installation errors:

1. **Upgrade pip**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install system dependencies** (macOS):
   ```bash
   brew install postgresql libpq
   ```

3. **Install system dependencies** (Ubuntu):
   ```bash
   sudo apt-get install python3-dev libpq-dev
   ```

### Database Issues

If migrations fail:

```bash
# Drop and recreate database (WARNING: destroys all data)
python manage.py reset_db
python manage.py migrate
```

### Import Errors

If you get import errors for custom modules:

```bash
# Make sure you're in the project root
cd /path/to/nexus

# Run with proper Python path
PYTHONPATH=. python manage.py runserver
```

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code with black
black .

# Sort imports
isort .

# Check code quality
flake8
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Shell

```bash
python manage.py shell_plus
```

## Minimal Working Setup (No External Services)

For the absolute minimal setup without Redis, Celery, or external APIs:

1. Use SQLite database:
   ```
   DATABASE_URL=sqlite:///db.sqlite3
   ```

2. Use console email backend (already default):
   ```
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

3. Skip Redis/Celery setup - async tasks will fail but the app will run

4. Comment out Celery in settings if needed

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api-playground/
- API Schema: http://localhost:8000/schema/

## Next Steps

1. Explore the admin panel at /admin
2. Check out the API at /api/
3. Create some test data
4. Review the implemented features in the codebase

## Need Help?

Check the Django documentation: https://docs.djangoproject.com/
