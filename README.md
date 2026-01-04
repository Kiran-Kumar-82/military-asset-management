# Military Asset Management System

A comprehensive Django-based system for tracking military assets, managing transfers between bases, recording purchases and expenditures, and maintaining complete audit trails for accountability and transparency.

## Features

### Core Functionality
✅ **Asset Tracking**: Track opening balances, closing balances, and net movements  
✅ **Purchases Management**: Record and approve asset purchases  
✅ **Inter-Base Transfers**: Facilitate and track asset transfers with history  
✅ **Personnel Assignments**: Assign assets to personnel with return tracking  
✅ **Expenditure Recording**: Track consumed/expended assets  
✅ **Complete Audit Trail**: Comprehensive transaction logging for accountability  

### Dashboard
- Key metrics display (Opening, Closing, Assigned, Expended balances)
- Real-time asset inventory overview
- Filterable by base and equipment type
- Recent transaction history
- Net movement details with breakdown (Purchases, Transfers In/Out)

### Role-Based Access Control (RBAC)
- **Admin**: Full system access
- **Base Commander**: Access to assigned base only
- **Logistics Officer**: Multi-base access with operational restrictions

### Security Features
- CSRF protection
- SQL injection prevention
- XSS protection via template auto-escaping
- Role-based authorization
- Complete audit logging
- Secure password handling
- IP address logging in transactions

## Technology Stack

### Backend
- Django 5.2.9
- PostgreSQL (production)
- SQLite (development)
- Gunicorn (WSGI server)
- WhiteNoise (static file serving)

### Frontend
- Django Templates
- Bootstrap 5.3
- Font Awesome 6.4
- jQuery 3.6

### Deployment
- Render (free tier compatible)
- Environment-based configuration
- Automated migrations

## Project Structure

```
military/
├── military_config/          # Django project settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── middleware.py        # Audit logging middleware
├── assets/                   # Main application
│   ├── models.py            # Database models
│   ├── views.py             # Request handlers
│   ├── forms.py             # Form definitions
│   ├── admin.py             # Admin interface
│   ├── urls.py              # App URL patterns
│   └── migrations/          # Database migrations
├── accounts/                 # Authentication app
│   ├── models.py            # User extensions
│   └── urls.py              # Auth URL patterns
├── tracking/                 # Tracking app (extensible)
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── assets/              # Asset app templates
│   └── accounts/            # Auth templates
├── staticfiles/             # Collected static files
├── logs/                    # Application logs
├── manage.py                # Django CLI
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── Procfile                 # Render process definition
├── build.sh                 # Build script
├── DEPLOYMENT.md            # Detailed deployment guide
└── README.md                # This file
```

## Quick Start

### Local Development

1. **Clone repository**
```bash
git clone <repository-url>
cd military
```

2. **Setup virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=sqlite
```

5. **Initialize database**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access application**
- Application: http://localhost:8000
- Admin: http://localhost:8000/admin/
- Login: http://localhost:8000/accounts/login/

### Test Credentials
Use Django admin to create test users with different roles.

## Database Models

### Base
Military base/installation with location and commander assignment.

### EquipmentType
Equipment categories (Vehicle, Weapon, Ammunition, Other) with unit of measure.

### Asset
Inventory record per base with opening/closing balances and movement tracking.

### Purchase
Asset purchases with supplier info and approval workflow (Pending → Approved/Rejected).

### Transfer
Inter-base asset transfers with status tracking (Pending → In Transit → Completed).

### Assignment
Personnel asset assignments with return tracking.

### Expenditure
Consumed/expended asset records with reason tracking.

### TransactionLog
Complete audit trail with user, timestamp, quantity, and IP address.

## API Endpoints

### Public (Unauthenticated)
- `POST /accounts/login/` - User login
- `GET /accounts/logout/` - User logout

### Authenticated
- `GET /` - Dashboard
- `GET /purchases/` - Purchase list & form
- `GET /transfers/` - Transfer list & form
- `GET /assignments/` - Assignment list & form
- `GET /expenditures/` - Expenditure list & form
- `POST /purchases/<id>/approve/` - Approve purchase
- `POST /transfers/<id>/complete/` - Complete transfer
- `POST /assignments/<id>/return/` - Return assignment

### Admin Only
- `GET /transactions/` - Complete transaction audit log
- `GET /admin/` - Django admin interface

## Configuration

### Environment Variables
```env
# Security
SECRET_KEY=your-super-secret-key
DEBUG=True|False

# Database (SQLite)
DB_ENGINE=sqlite

# Database (PostgreSQL)
DB_ENGINE=postgresql
DB_NAME=database_name
DB_USER=username
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Hosting
ALLOWED_HOSTS=localhost,yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000

# SSL (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Deployment

### Render Deployment (Free Tier)
See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

**Key Steps:**
1. Push to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service connected to GitHub
4. Set environment variables
5. Deploy and run migrations
6. Access at `your-app.onrender.com`

## User Roles & Permissions

### Admin
- View all data across all bases
- Approve purchases and transfers
- Manage users and permissions
- View audit logs

### Base Commander
- View only their assigned base
- Create and manage operations within base
- Limited purchase/transfer management

### Logistics Officer
- View data across multiple bases
- Manage purchases and transfers
- Cannot manage users

## Audit & Compliance

Every action is logged with:
- Transaction type
- Asset and quantity
- User performing action
- Timestamp
- IP address
- Status changes

Access through:
- Admin: Transaction Log page
- Logs directory: `logs/audit.log`

## Performance Optimization

- Database query optimization with select_related/prefetch_related
- Static file compression via WhiteNoise
- Pagination for large datasets
- Indexed fields for frequent queries
- Caching middleware ready for Redis

## Security Considerations

- ✅ CSRF token protection
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection
- ✅ Secure password hashing
- ✅ Session security
- ✅ Role-based access control
- ✅ Audit logging
- ✅ Environment variable secrets

**Production Checklist:**
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS (SECURE_SSL_REDIRECT=True)
- [ ] Use PostgreSQL
- [ ] Set strong database password
- [ ] Enable secure cookies
- [ ] Configure CORS properly
- [ ] Set up regular backups
- [ ] Monitor logs regularly

## Troubleshooting

### Migration Issues
```bash
python manage.py migrate --verbose
python manage.py migrate assets --zero  # Rollback if needed
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Permission Denied
- Verify user is in correct group
- Check view permission requirements
- Review RBAC configuration in admin

### Database Connection Error
- Verify DB_* environment variables
- Check database service is running
- Ensure credentials are correct

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `python manage.py test`
4. Commit and push
5. Create pull request

## License

Military Asset Management System

## Support

For issues and questions:
1. Check DEPLOYMENT.md
2. Review Django documentation
3. Check Render documentation
4. Review audit logs for transaction details

## Version History

### v1.0.0 (Current)
- Initial release
- Core asset tracking
- RBAC implementation
- Audit logging
- Render deployment ready

## Next Steps

1. **Customize**: Modify models, views, and templates for specific needs
2. **Deploy**: Follow DEPLOYMENT.md for production setup
3. **Configure**: Set up bases, equipment types, and initial data
4. **Monitor**: Review logs regularly and maintain backups
5. **Extend**: Add additional features using provided foundation

---

**Built with Django for secure, transparent military asset management.**
