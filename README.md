# Military Asset Management System (MAMS)

A comprehensive, secure, and scalable system for managing military assets across multiple bases. Built with Django REST Framework backend and React frontend.

## 🏗️ Architecture Overview

### Technology Stack

**Backend:**
- Django 4.2.7
- Django REST Framework
- JWT Authentication (Simple JWT)
- SQLite (local development)
- PostgreSQL (production)
- Gunicorn (production server)

**Frontend:**
- React 18
- Material-UI (MUI)
- React Router
- Axios
- Vite

**Deployment:**
- Backend: Render
- Frontend: Vercel

## 📊 Database Schema

### Core Models

1. **Base** - Military bases
   - name, code, location, description

2. **AssetType** - Types of assets (vehicles, weapons, ammunition)
   - name, category, description, unit

3. **Asset** - Current inventory per base and asset type
   - base, asset_type, quantity

4. **Purchase** - Asset purchases
   - base, asset_type, quantity, purchase_date, purchase_cost, supplier

5. **Transfer** - Asset transfers between bases
   - source_base, destination_base, asset_type, quantity, transfer_date

6. **Assignment** - Assets assigned to personnel/units
   - base, asset_type, quantity, assigned_to, assignment_date, status

7. **Expenditure** - Assets expended/consumed
   - base, asset_type, quantity, expenditure_date, reason

8. **AuditLog** - Immutable audit trail
   - action, model_name, object_id, details, user, timestamp

### Relationships

- User → Role (Many-to-One)
- User → Base (Many-to-One, for Base Commanders)
- Asset → Base + AssetType (Many-to-One each, unique together)
- Purchase/Transfer/Assignment/Expenditure → Base + AssetType (Many-to-One each)

## 🔐 Role-Based Access Control (RBAC)

### Roles

1. **Admin**
   - Full system access
   - Can manage users, bases, asset types
   - Can view all bases and audit logs

2. **Base Commander**
   - Access only to their assigned base
   - Can view dashboard, inventory, assignments, expenditures for their base
   - Cannot create purchases or transfers

3. **Logistics Officer**
   - Can create and manage purchases and transfers
   - Can view all bases
   - Cannot access user management

### Permission Enforcement

- View-level permissions using custom permission classes
- Middleware for additional security layer
- Query filtering based on user role

## 📈 Dashboard Metrics

The dashboard calculates and displays:

- **Opening Balance**: Inventory at start of date range
- **Closing Balance**: Inventory at end of date range
- **Net Movement**: Purchases + Transfers In - Transfers Out
- **Assigned Assets**: Currently assigned assets
- **Expended Assets**: Assets consumed in date range

Net Movement details (clickable):
- Purchases
- Transfers In
- Transfers Out

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Update `.env` with your settings (for local development, USE_SQLITE=True is fine)

6. Run migrations:
```bash
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Create initial roles (run in Django shell):
```python
python manage.py shell
>>> from accounts.models import Role
>>> Role.objects.create(name='admin', description='System Administrator')
>>> Role.objects.create(name='base_commander', description='Base Commander')
>>> Role.objects.create(name='logistics_officer', description='Logistics Officer')
```

9. Start development server:
```bash
python manage.py runserver
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000/api
```

5. Start development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## 🌐 Deployment

### Backend Deployment (Render)

1. **Create a new Web Service on Render:**
   - Connect your GitHub repository
   - Select the `backend` directory as root
   - Choose Python environment

2. **Configure Environment Variables:**
   ```
   SECRET_KEY=<generate-a-secure-secret-key>
   DEBUG=False
   USE_SQLITE=False
   DB_NAME=<from-postgres-database>
   DB_USER=<from-postgres-database>
   DB_PASSWORD=<from-postgres-database>
   DB_HOST=<from-postgres-database>
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

3. **Create PostgreSQL Database:**
   - Create a new PostgreSQL database on Render
   - Note the connection details

4. **Build Settings:**
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn mams.wsgi:application`

5. **Deploy:**
   - Render will automatically deploy on push to main branch

### Frontend Deployment (Vercel)

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
cd frontend
vercel
```

3. **Configure Environment Variables:**
   - In Vercel dashboard, add:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api
   ```

4. **Update CORS in Backend:**
   - Update `CORS_ALLOWED_ORIGINS` in backend `.env` to include your Vercel URL

## 📝 API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Accounts
- `GET /api/accounts/users/` - List users (Admin only)
- `GET /api/accounts/users/profile/` - Get current user profile
- `PUT /api/accounts/users/profile/` - Update current user profile

### Assets
- `GET /api/assets/bases/` - List bases
- `GET /api/assets/asset-types/` - List asset types
- `GET /api/assets/inventory/` - List inventory
- `GET /api/assets/dashboard/data/` - Get dashboard data

### Purchases
- `GET /api/assets/purchases/` - List purchases
- `POST /api/assets/purchases/` - Create purchase
- `PUT /api/assets/purchases/{id}/` - Update purchase
- `DELETE /api/assets/purchases/{id}/` - Delete purchase

### Transfers
- `GET /api/assets/transfers/` - List transfers
- `POST /api/assets/transfers/` - Create transfer
- `PUT /api/assets/transfers/{id}/` - Update transfer
- `DELETE /api/assets/transfers/{id}/` - Delete transfer

### Assignments
- `GET /api/assets/assignments/` - List assignments
- `POST /api/assets/assignments/` - Create assignment
- `PUT /api/assets/assignments/{id}/` - Update assignment
- `DELETE /api/assets/assignments/{id}/` - Delete assignment

### Expenditures
- `GET /api/assets/expenditures/` - List expenditures
- `POST /api/assets/expenditures/` - Create expenditure
- `PUT /api/assets/expenditures/{id}/` - Update expenditure
- `DELETE /api/assets/expenditures/{id}/` - Delete expenditure

### Audit Logs
- `GET /api/audit/logs/` - List audit logs (Admin only)

## 🔒 Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **RBAC**: Role-based access control at multiple levels
3. **Audit Logging**: All changes are logged immutably
4. **CORS Protection**: Configured for specific origins
5. **Input Validation**: Django model and serializer validation
6. **SQL Injection Protection**: Django ORM prevents SQL injection
7. **XSS Protection**: React automatically escapes content

## 📋 Testing Checklist

- [ ] User authentication and authorization
- [ ] Role-based access control
- [ ] Dashboard calculations
- [ ] Purchase creation and inventory update
- [ ] Transfer creation and inventory update
- [ ] Assignment tracking
- [ ] Expenditure recording
- [ ] Audit log generation
- [ ] Date range filtering
- [ ] Base and asset type filtering

## 🐛 Troubleshooting

### Backend Issues

1. **Database connection errors:**
   - Check `.env` file configuration
   - Verify database credentials
   - Ensure database is running

2. **Migration errors:**
   - Run `python manage.py makemigrations`
   - Then `python manage.py migrate`

3. **CORS errors:**
   - Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL

### Frontend Issues

1. **API connection errors:**
   - Check `VITE_API_URL` in `.env`
   - Verify backend is running
   - Check browser console for errors

2. **Authentication errors:**
   - Clear localStorage
   - Re-login
   - Check token expiration

## 📚 Additional Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational/demonstration purposes.

## 🎯 Future Enhancements

- Real-time notifications
- Advanced reporting and analytics
- Mobile app (React Native)
- Barcode/QR code scanning
- Integration with external systems
- Advanced search and filtering
- Export to PDF/Excel
- Email notifications

---

**Note**: This system is designed for demonstration purposes. For production use, ensure:
- Strong secret keys
- HTTPS only
- Regular security audits
- Database backups
- Monitoring and logging
- Rate limiting
- Additional security hardening


