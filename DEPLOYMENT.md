# Military Asset Management System - Deployment Guide

## Overview
This is a comprehensive Military Asset Management System built with Django and PostgreSQL. This guide provides step-by-step instructions for deploying to Render's free tier.

## Prerequisites
- GitHub account with the project repository
- Render account (free tier)
- PostgreSQL database (Render provides free tier)

## Local Development Setup

### 1. Clone and Setup
```bash
git clone <your-repository>
cd military
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.onrender.com
DB_ENGINE=sqlite
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Access at `http://localhost:8000`

## Deployment to Render

### Step 1: Prepare Your Repository
Ensure these files are in your repository:
- `requirements.txt`
- `.env.example` (template for environment variables, not actual secrets)
- `Procfile`
- `build.sh` (build script)

### Step 2: Create Procfile
Create `Procfile` in the root directory:
```
web: gunicorn military_config.wsgi:application --log-file -
worker: python manage.py process_tasks
release: python manage.py migrate
```

### Step 3: Create build.sh
Create `build.sh` in the root directory:
```bash
#!/bin/bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
```

Make it executable:
```bash
chmod +x build.sh
```

### Step 4: Create PostgreSQL Database on Render

1. Log in to Render dashboard
2. Click "New" → "PostgreSQL"
3. Choose:
   - **Name**: military-assets-db
   - **Database**: military_assets
   - **User**: postgres (or custom)
   - **Region**: Choose closest to you
   - **Version**: 14 or latest
4. Create database and copy the connection string

### Step 5: Deploy Web Service on Render

1. Push your code to GitHub
2. Go to Render dashboard
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: military-assets
   - **Environment**: Python 3.11
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn military_config.wsgi:application --log-file -`

### Step 6: Set Environment Variables on Render

Add these in the "Environment" section:

```
SECRET_KEY=<generate a random secure key>
DEBUG=False
ALLOWED_HOSTS=military-assets.onrender.com,yourdomain.com
DB_ENGINE=postgresql
DB_NAME=military_assets
DB_USER=postgres
DB_PASSWORD=<from PostgreSQL service>
DB_HOST=<from PostgreSQL service>
DB_PORT=5432
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://military-assets.onrender.com
```

### Step 7: Deploy
Click "Deploy" and wait for the deployment to complete.

## Post-Deployment

### 1. Create Admin User
After deployment, run in Render shell:
```bash
python manage.py createsuperuser
```

### 2. Verify Deployment
- Visit: `https://military-assets.onrender.com`
- Login at: `https://military-assets.onrender.com/accounts/login/`
- Admin panel: `https://military-assets.onrender.com/admin/`

### 3. Create Initial Data
Use the admin panel to:
1. Create military bases
2. Create equipment types
3. Create initial assets with opening balances

## Database Schema

### Core Models

#### Base
- Military base/installation
- Fields: name, location, commander

#### EquipmentType
- Equipment categories (Vehicle, Weapon, Ammunition, etc.)
- Fields: name, category, description, unit_of_measure

#### Asset
- Individual asset inventory per base
- Fields: equipment_type, base, opening_balance, closing_balance, assigned_count, expended_count

#### Purchase
- Track asset purchases with approval workflow
- Fields: asset, quantity, supplier, cost, status, reference_number

#### Transfer
- Track transfers between bases
- Fields: equipment_type, quantity, from_base, to_base, status

#### Assignment
- Track asset assignments to personnel
- Fields: asset, personnel, quantity, assignment_date, return_date

#### Expenditure
- Track expended/consumed assets
- Fields: asset, quantity, reason, reference_number

#### TransactionLog
- Complete audit trail of all operations
- Fields: asset, transaction_type, quantity, created_by, created_at, ip_address

## Role-Based Access Control (RBAC)

### Roles Implemented

#### 1. Admin
- Full system access
- Can approve purchases and transfers
- Access to audit logs
- Can manage all users and bases

#### 2. Base Commander
- Access to data for their assigned base only
- Can record purchases, transfers, assignments
- Can view their base's inventory

#### 3. Logistics Officer
- Access to all bases' data
- Can manage purchases and transfers
- Cannot modify user permissions

### Creating Roles
Use Django admin panel:
1. Go to Groups
2. Create groups: Admin, Base Commander, Logistics Officer
3. Assign permissions as needed

## API Endpoints

### Authentication
- `GET /accounts/login/` - Login page
- `POST /accounts/login/` - Login submission
- `GET /accounts/logout/` - Logout

### Dashboard & Inventory
- `GET /` - Dashboard
- `GET /assets/<id>/` - Asset details
- `GET /assets/<id>/net-movement/` - Net movement details (JSON)

### Purchases
- `GET /purchases/` - Purchase list
- `POST /purchases/` - Create purchase
- `POST /purchases/<id>/approve/` - Approve purchase

### Transfers
- `GET /transfers/` - Transfer list
- `POST /transfers/` - Create transfer
- `POST /transfers/<id>/complete/` - Complete transfer

### Assignments
- `GET /assignments/` - Assignment list
- `POST /assignments/` - Create assignment
- `POST /assignments/<id>/return/` - Return assignment

### Expenditures
- `GET /expenditures/` - Expenditure list
- `POST /expenditures/` - Record expenditure

### Audit
- `GET /transactions/` - Transaction log (Admin only)

## Security Features

### Implemented
- CSRF protection (Django built-in)
- SQL injection prevention (Django ORM)
- XSS protection (template auto-escaping)
- Role-based access control
- Audit logging of all transactions
- Secure password hashing
- Session security
- SSL/TLS on production

### Database Connection
- PostgreSQL with encrypted connections
- Environment variable secrets management
- No hardcoded credentials

## Monitoring & Logging

### Log Files
- `/logs/django.log` - Application logs
- `/logs/audit.log` - Transaction audit trail

### Render Dashboard
- Monitor uptime
- View deployment logs
- Check resource usage
- Database backups

## Troubleshooting

### Build Fails
1. Check build logs in Render
2. Verify all dependencies in requirements.txt
3. Ensure .env variables are set

### Migration Errors
1. SSH into Render web service
2. Run: `python manage.py migrate --verbose`
3. Check database connection

### Static Files Not Loading
1. Run: `python manage.py collectstatic --noinput`
2. Verify STATIC_ROOT setting
3. Check Render's file system mount

### Database Connection Issues
1. Verify DATABASE_URL format
2. Check PostgreSQL service is running
3. Ensure credentials are correct

## Scaling & Optimization

### For Higher Load
1. **Database**: Upgrade PostgreSQL plan
2. **Web Dyno**: Increase instance type
3. **Caching**: Add Redis for session caching
4. **CDN**: Serve static files via CDN
5. **Background Tasks**: Use Celery for async operations

### Performance Tips
- Index frequently queried fields
- Enable query caching
- Optimize database queries (use select_related, prefetch_related)
- Minimize template rendering
- Compress static files (whitenoise handles this)

## Maintenance

### Regular Tasks
- Monitor application logs weekly
- Review transaction logs monthly
- Test database backups
- Update dependencies quarterly
- Review security settings regularly

### Backup Strategy
- Render provides daily automated backups
- Export critical data monthly
- Keep encrypted backups off-site
- Test restore procedures

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Render Documentation: https://render.com/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/

## License
Military Asset Management System

## Version
1.0.0 - Initial Release
