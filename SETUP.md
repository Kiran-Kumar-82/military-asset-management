# Quick Setup Guide

## Initial Setup Steps

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and set SECRET_KEY (generate a random key)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Set up initial data (roles, sample bases, asset types)
python manage.py shell < setup_initial_data.py

# Start server
python manage.py runserver
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env and set VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

### 3. First Login

1. Go to http://localhost:3000
2. Login with your superuser credentials
3. Go to Django admin (http://localhost:8000/admin) to:
   - Assign roles to users
   - Assign bases to Base Commanders
   - Create additional bases and asset types

## Creating Test Users

### Via Django Admin

1. Go to http://localhost:8000/admin
2. Navigate to Users
3. Create new users
4. Assign roles and bases (for Base Commanders)

### Via API (after login as admin)

```bash
# Create a Base Commander
curl -X POST http://localhost:8000/api/accounts/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "commander1",
    "email": "commander1@example.com",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "first_name": "John",
    "last_name": "Commander",
    "role": 2,
    "assigned_base": 1
  }'
```

## Testing the System

1. **Login** as different user roles
2. **Create a Purchase** (as Admin or Logistics Officer)
3. **Create a Transfer** (as Admin or Logistics Officer)
4. **View Dashboard** - check calculations
5. **Create Assignment** (any authenticated user)
6. **Create Expenditure** (any authenticated user)
7. **View Audit Logs** (Admin only)

## Common Issues

### Database locked (SQLite)
- Close any other processes accessing the database
- Restart the Django server

### CORS errors
- Check CORS_ALLOWED_ORIGINS in backend/.env
- Ensure it includes http://localhost:3000

### Module not found
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Date picker not working
- Ensure @mui/x-date-pickers is installed: `npm install @mui/x-date-pickers`
- Check browser console for errors


