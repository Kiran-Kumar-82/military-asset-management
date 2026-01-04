# Military Asset Management System - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (recommended)

### Step 1: Clone & Setup Environment
```bash
cd c:\Users\kiran\Desktop\military
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Mac/Linux
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python manage.py migrate
python manage.py setup_initial_data
python manage.py collectstatic --noinput
```

### Step 4: Start Development Server
```bash
python manage.py runserver
```

### Step 5: Access Application
- **Application URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Login Page**: http://localhost:8000/accounts/login/

## 📋 Demo Credentials

### Admin User
- **Username**: admin
- **Password**: admin123
- **Access**: Full system access, all bases, all operations

### Base Commander
- **Username**: commander
- **Password**: pass123
- **Access**: Limited to assigned base operations

### Logistics Officer
- **Username**: logistics
- **Password**: pass123
- **Access**: Multi-base operations management

## 🎯 First Steps

### 1. Create Your First Asset (Admin)
1. Login as admin at http://localhost:8000/accounts/login/
2. Go to Admin Panel (`/admin/`)
3. Click "Assets" → "Add Asset"
4. Select:
   - Equipment Type (e.g., "M4 Carbine")
   - Base (e.g., "Fort Liberty")
   - Opening Balance (e.g., 100)
5. Click "Save"
6. The system will auto-calculate closing balance

### 2. Record a Purchase
1. Go to Purchases page (left menu)
2. Click "New Purchase"
3. Fill in:
   - Equipment: M4 Carbine
   - Quantity: 50
   - Supplier: MilTech Supply
   - Reference: PO-2026-001
   - Cost: $50,000
4. Submit and wait for admin approval

### 3. Request Transfer
1. Go to Transfers page
2. Click "New Transfer"
3. Select:
   - Equipment: M4 Carbine
   - Quantity: 25
   - From Base: Fort Liberty
   - To Base: Fort Jackson
4. Submit transfer

### 4. Assign to Personnel
1. Go to Assignments page
2. Click "New Assignment"
3. Select:
   - Equipment: M4 Carbine
   - Personnel: Choose someone
   - Quantity: 10
4. Submit assignment

### 5. Record Expenditure
1. Go to Expenditures page
2. Click "Record Expenditure"
3. Fill in:
   - Equipment: 5.56mm Ammunition
   - Quantity: 10000
   - Reason: Training Exercise
4. Submit

## 📊 Dashboard Metrics

The dashboard shows:
- **Opening Balance**: Initial asset count
- **Closing Balance**: Current inventory after all transactions
- **Assigned**: Assets assigned to personnel
- **Expended**: Assets consumed/destroyed

**Formula**: Closing = Opening + Purchases + Transfers In - Transfers Out - Assigned - Expended

## 🔐 Access Control

### Admin Can:
- ✅ View all data
- ✅ Approve purchases
- ✅ Complete transfers
- ✅ Manage users
- ✅ View audit logs

### Base Commander Can:
- ✅ View base inventory
- ✅ Request purchases/transfers
- ✅ Assign assets
- ✅ Record expenditures
- ❌ Cannot approve (needs admin)
- ❌ Cannot access other bases

### Logistics Officer Can:
- ✅ View all bases
- ✅ Manage purchases/transfers
- ✅ View trends
- ❌ Cannot manage users
- ❌ Cannot approve final actions

## 📁 Project Structure

```
military/
├── military_config/    - Django configuration
├── assets/            - Main application
├── accounts/          - Authentication
├── templates/         - HTML templates
├── staticfiles/       - CSS, JavaScript, Images
├── logs/              - Application logs
├── manage.py          - Django CLI
└── README.md          - Full documentation
```

## 🔧 Common Tasks

### View All Assets
1. Go to Dashboard
2. Scroll down to "Asset Inventory" table

### Filter Assets by Base
1. Use dropdown filters on Dashboard
2. Select base and click "Apply Filters"

### View Transaction History
1. Go to Admin → Transaction Log (admin only)
2. Or view asset-specific history in Asset Details

### Approve Purchase
1. Admin goes to Purchases page
2. Click "Approve" button on pending purchase

### Create New Personnel
1. Go to Admin → Personnel → Add Personnel
2. Link to existing Django user or create new
3. Set rank and service number

### Export Data
1. Admin panel allows CSV export
2. Use Python script for custom export

## ⚙️ Configuration

### Change DEBUG Mode
Edit `.env`:
```env
DEBUG=False  # Production
DEBUG=True   # Development
```

### Change Database
Edit `.env` for PostgreSQL:
```env
DB_ENGINE=postgresql
DB_NAME=military_assets
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Add Allowed Hosts
Edit `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Database Locked
```bash
rm db.sqlite3  # Delete SQLite database
python manage.py migrate  # Reinitialize
python manage.py setup_initial_data
```

### Missing Migrations
```bash
python manage.py migrate --verbose
python manage.py migrate assets
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

## 📚 Documentation

- **Full Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Complete README**: See [README.md](README.md)
- **Django Docs**: https://docs.djangoproject.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/

## 🚀 Next Steps

1. **Customize**: Modify templates in `templates/assets/`
2. **Add Features**: Extend models and views
3. **Deploy**: Follow DEPLOYMENT.md for Render
4. **Backup**: Regular database backups
5. **Monitor**: Check logs in `logs/` directory

## ⚠️ Security Notes

### Before Production
- [ ] Change SECRET_KEY in `.env`
- [ ] Change DEBUG to False
- [ ] Change admin password
- [ ] Change commander and logistics passwords
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS
- [ ] Configure SECURE_SSL_REDIRECT
- [ ] Set up database backups

### Passwords
```bash
# Change any user password
python manage.py changepassword username
```

## 📞 Support

If you encounter issues:
1. Check application logs: `logs/django.log`
2. Review audit trail: `logs/audit.log`
3. Visit Django documentation
4. Check project README for detailed info

## ✨ Features to Explore

- 📊 Interactive dashboard with real-time metrics
- 🔐 Role-based access control system
- 📝 Complete audit trail and transaction logging
- 🔄 Inter-base transfer management
- 👤 Personnel asset assignment tracking
- 📋 Approval workflows for purchases/transfers
- 🏢 Multi-base support
- 🗂️ Equipment type categorization

---

**Happy tracking! For more details, see README.md and DEPLOYMENT.md**
