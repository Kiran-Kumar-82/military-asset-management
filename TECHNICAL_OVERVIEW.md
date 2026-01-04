# Military Asset Management System - Technical Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser / Client                      │
└──────────────────────────┬──────────────────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Web Application (Gunicorn)               │
├─────────────────────────────────────────────────────────────┤
│ Apps: assets, accounts, tracking (extensible)               │
├─────────────────────────────────────────────────────────────┤
│ Middleware:                                                  │
│  • Security (CSRF, XSS, Clickjacking protection)           │
│  • CORS Headers                                             │
│  • Audit Logging (request tracking)                         │
│  • WhiteNoise (static file serving)                         │
├─────────────────────────────────────────────────────────────┤
│ Features:                                                    │
│  • Role-Based Access Control (RBAC)                        │
│  • Transaction Logging                                      │
│  • Asset Tracking with balances                            │
│  • Purchase/Transfer/Assignment workflows                  │
│  • Admin Interface                                          │
└──────────────────────────┬──────────────────────────────────┘
                          │ SQL
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Production)                │
│              SQLite Database (Development)                   │
├─────────────────────────────────────────────────────────────┤
│ Tables:                                                      │
│  • assets_base (military bases)                            │
│  • assets_equipment_type                                    │
│  • assets_asset (inventory)                                │
│  • assets_purchase (procurement)                           │
│  • assets_transfer (inter-base transfers)                  │
│  • assets_assignment (personnel assignments)              │
│  • assets_expenditure (consumption)                        │
│  • assets_transactionlog (audit trail)                     │
│  • auth_user (user accounts)                               │
│  • auth_group (roles)                                      │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### User & Authentication
```
┌─ User (Django Auth)
│  ├─ id: PK
│  ├─ username
│  ├─ password (hashed)
│  ├─ email
│  └─ groups (M2M to Group)
│
└─ Group (Roles)
   ├─ id: PK
   ├─ name (Admin, Base Commander, Logistics Officer)
   └─ permissions (M2M)
```

### Asset Management
```
┌─ Base
│  ├─ id: PK
│  ├─ name: CharField(255, unique)
│  ├─ location: CharField(255)
│  ├─ commander: FK to User (nullable)
│  └─ timestamps
│
├─ EquipmentType
│  ├─ id: PK
│  ├─ name: CharField(255, unique)
│  ├─ category: VEHICLE|WEAPON|AMMUNITION|OTHER
│  ├─ description
│  ├─ unit_of_measure
│  └─ timestamps
│
├─ Asset (one per equipment per base)
│  ├─ id: PK
│  ├─ equipment_type: FK to EquipmentType
│  ├─ base: FK to Base
│  ├─ opening_balance: DecimalField
│  ├─ closing_balance: DecimalField (auto-calculated)
│  ├─ assigned_count: DecimalField
│  ├─ expended_count: DecimalField
│  └─ timestamps
│
└─ Personnel
   ├─ id: PK
   ├─ user: OneToOne to User
   ├─ base: FK to Base
   ├─ rank: CharField
   ├─ service_number: CharField(unique)
   └─ timestamps
```

### Transactions
```
┌─ Purchase
│  ├─ id: PK
│  ├─ asset: FK to Asset
│  ├─ quantity: DecimalField
│  ├─ supplier: CharField
│  ├─ reference_number: CharField(unique)
│  ├─ cost: DecimalField
│  ├─ status: PENDING|APPROVED|REJECTED
│  ├─ created_by: FK to User
│  ├─ approved_by: FK to User (nullable)
│  └─ timestamps
│
├─ Transfer
│  ├─ id: PK
│  ├─ equipment_type: FK to EquipmentType
│  ├─ quantity: DecimalField
│  ├─ from_base: FK to Base
│  ├─ to_base: FK to Base
│  ├─ reference_number: CharField(unique)
│  ├─ status: PENDING|IN_TRANSIT|COMPLETED|REJECTED
│  ├─ initiated_by: FK to User
│  ├─ approved_by: FK to User (nullable)
│  └─ timestamps
│
├─ TransferLog
│  ├─ id: PK
│  ├─ asset: FK to Asset
│  ├─ transfer: FK to Transfer
│  ├─ transfer_type: IN|OUT
│  ├─ quantity: DecimalField
│  ├─ status: PENDING|COMPLETED|REJECTED
│  └─ timestamps
│
├─ Assignment
│  ├─ id: PK
│  ├─ asset: FK to Asset
│  ├─ personnel: FK to Personnel
│  ├─ quantity: DecimalField
│  ├─ assignment_date: DateTimeField
│  ├─ return_date: DateTimeField (nullable)
│  ├─ assigned_by: FK to User
│  └─ timestamps
│
├─ Expenditure
│  ├─ id: PK
│  ├─ asset: FK to Asset
│  ├─ quantity: DecimalField
│  ├─ reason: CharField
│  ├─ reference_number: CharField(unique)
│  ├─ recorded_by: FK to User
│  └─ timestamps
│
└─ TransactionLog (Audit Trail)
   ├─ id: PK
   ├─ asset: FK to Asset
   ├─ transaction_type: PURCHASE|TRANSFER_IN|TRANSFER_OUT|ASSIGNMENT|EXPENDITURE
   ├─ quantity: DecimalField
   ├─ related_object_id: IntegerField (FK to originating object)
   ├─ created_by: FK to User
   ├─ created_at: DateTimeField
   ├─ ip_address: GenericIPAddressField
   └─ user_agent: TextField
```

## Data Relationships

### Asset Balance Calculation
```
Closing Balance = 
    Opening Balance 
    + Sum(Approved Purchases)
    + Sum(Completed Transfer Ins)
    - Sum(Completed Transfer Outs)
    - Sum(Active Assignments)
    - Sum(Expenditures)
```

### Automatic Updates
1. **Purchase Created**: status=PENDING, not reflected in balance
2. **Purchase Approved**: closing_balance updated, TransactionLog created
3. **Transfer Initiated**: TransferLog created
4. **Transfer Completed**: Both bases' balances updated, TransactionLogs created
5. **Assignment Created**: assigned_count increased, closing_balance reduced
6. **Assignment Returned**: assigned_count decreased, closing_balance increased
7. **Expenditure Recorded**: expended_count increased, closing_balance reduced

## Role-Based Access Control (RBAC)

### Authorization Matrix

| Operation | Admin | Base Commander | Logistics Officer |
|-----------|-------|-----------------|-------------------|
| View All Bases | ✅ | ❌ | ✅ |
| View Own Base | ✅ | ✅ | ✅ |
| Create Purchase | ✅ | ✅ | ✅ |
| Approve Purchase | ✅ | ❌ | ❌ |
| Create Transfer | ✅ | ✅ | ✅ |
| Complete Transfer | ✅ | ❌ | ❌ |
| Create Assignment | ✅ | ✅ | ❌ |
| Record Expenditure | ✅ | ✅ | ❌ |
| View Audit Log | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| Access Admin Panel | ✅ | ❌ | ❌ |

### Implementation
- Django's built-in Group and Permission system
- Decorators: `@login_required`, `@permission_required`
- Custom helper functions: `get_user_base()`, `filter_assets_for_user()`
- View-level checks: `user.is_superuser`, `user.groups.filter()`

## API Response Formats

### Dashboard Metrics (JSON embedded in HTML)
```json
{
  "total_opening_balance": 1000,
  "total_closing_balance": 950,
  "total_assigned": 30,
  "total_expended": 20
}
```

### Net Movement Details API
```json
{
  "asset": "M4 Carbine at Fort Liberty",
  "purchases": [
    {
      "id": 1,
      "quantity": 100,
      "supplier": "MilTech Supply",
      "purchase_date": "2026-01-01T10:00:00Z"
    }
  ],
  "transfers_in": [...],
  "transfers_out": [...],
  "net_movement": 100.0
}
```

## View Hierarchy

```
assets/
├── dashboard(request)
│   └── template: assets/dashboard.html
│
├── purchases(request)
│   ├── GET: template: assets/purchases.html
│   └── POST: Create purchase
│
├── approve_purchase(request, purchase_id)
│   └── POST: Approve and update balance
│
├── transfers(request)
│   ├── GET: template: assets/transfers.html
│   └── POST: Create transfer
│
├── complete_transfer(request, transfer_id)
│   └── POST: Complete and update both bases
│
├── assignments(request)
│   ├── GET: template: assets/assignments.html
│   └── POST: Create assignment
│
├── return_assignment(request, assignment_id)
│   └── POST: Return and update balance
│
├── expenditures(request)
│   ├── GET: template: assets/expenditures.html
│   └── POST: Record expenditure
│
├── asset_detail(request, asset_id)
│   └── template: assets/asset_detail.html
│
├── transaction_log(request)
│   └── template: assets/transaction_log.html
│
└── net_movement_detail(request, asset_id)
    └── JSON: Asset movement breakdown
```

## Request/Response Flow

### Create Purchase Flow
```
1. GET /purchases/
   └─ Render form with asset dropdown
   
2. POST /purchases/ with form data
   ├─ Check: user.is_superuser or logistics officer
   ├─ Check: base access (if commander)
   ├─ Save: Purchase(status=PENDING)
   └─ Redirect: /purchases/
   
3. Admin approves:
   POST /purchases/{id}/approve/
   ├─ Check: user.is_superuser
   ├─ Update: Purchase(status=APPROVED)
   ├─ Update: asset.closing_balance
   ├─ Create: TransactionLog
   └─ JSON Response: {"status": "success"}
```

### Transfer Flow
```
1. POST /transfers/ with form data
   ├─ Validate: from_base != to_base
   ├─ Save: Transfer(status=PENDING)
   ├─ Create: TransferLog(type=OUT, IN)
   └─ Redirect: /transfers/
   
2. Admin completes:
   POST /transfers/{id}/complete/
   ├─ Get: from_asset, to_asset
   ├─ Update: from_asset.closing_balance -= qty
   ├─ Update: to_asset.closing_balance += qty
   ├─ Update: Transfer(status=COMPLETED)
   ├─ Create: TransactionLog (both assets)
   └─ JSON Response: {"status": "success"}
```

## Audit Trail

### Transaction Logging
Every significant operation creates a TransactionLog entry:

```
TransactionLog.objects.create(
    asset=asset,
    transaction_type='PURCHASE',  # or TRANSFER_IN/OUT, ASSIGNMENT, EXPENDITURE
    quantity=amount,
    related_object_id=purchase_id,
    created_by=request.user,
    ip_address=client_ip,
    user_agent=request.META['HTTP_USER_AGENT']
)
```

### Audit File
- Location: `logs/audit.log`
- Format: Verbose timestamp, user, action, asset, quantity
- Retention: Rotating handler (15MB per file, 10 backups)

## Performance Optimizations

### Database Queries
- `select_related()`: Asset → Equipment, Base; Purchase → Asset, User
- `prefetch_related()`: Asset → Purchases, Transfers, Assignments
- Indexes on: (equipment_type, base), (created_by), (transaction_type)

### Caching (Ready for Redis)
- Session caching
- Template fragment caching
- QuerySet caching with django-redis

### Frontend
- WhiteNoise for static file compression
- Bootstrap CDN for CSS/JS
- Minimal inline JavaScript
- Form modal patterns to avoid page reloads

## Security Implementation

### CSRF Protection
- `{% csrf_token %}` in all POST forms
- `CsrfViewMiddleware` enabled
- Token validation on all mutating requests

### SQL Injection Prevention
- Django ORM prevents raw SQL injection
- Parameterized queries for all database access
- No string concatenation in queries

### XSS Protection
- Template auto-escaping enabled
- `{{ variable }}` auto-escaped
- `{{ variable|safe }}` only for trusted HTML

### Authentication
- Built-in Django User model
- Bcrypt/PBKDF2 password hashing
- Session-based authentication
- Login required decorators

### Authorization
- View-level permission checks
- Model-level access filtering
- User base restriction for commanders
- Admin-only functions protected

## Logging Configuration

### Application Logs (`logs/django.log`)
- Level: INFO
- Format: Timestamp, module, level, message
- Rotation: 15MB per file, 10 backups

### Audit Logs (`logs/audit.log`)
- Level: INFO
- Format: Verbose user/action/timestamp
- Rotation: 15MB per file, 10 backups

### Console Output
- Level: DEBUG (development)
- Format: Simple (level + message)

## Deployment Considerations

### Static Files
- Collected to `/staticfiles/`
- Served by WhiteNoise in production
- Can be offloaded to CDN

### Database Migrations
- Automatic in build.sh via `manage.py migrate`
- Safe for zero-downtime deployment
- Reversible if needed

### Environment Variables
- All secrets in .env
- Database credentials isolated
- API keys separated
- No defaults for production values

### WSGI Application
- Gunicorn: 4 workers, 2 threads each
- Configurable via Procfile
- Load balancer ready

## Extensibility Points

### Add Custom Fields to Asset
```python
# In assets/models.py Asset class
custom_metadata = models.JSONField(default=dict)
```

### Add New Equipment Categories
```python
# In EquipmentType.CATEGORY_CHOICES
('MEDICAL', 'Medical Equipment'),
('FUEL', 'Fuel & Energy'),
```

### Add Email Notifications
```python
# Use Django signals in models.py
from django.db.models.signals import post_save
@receiver(post_save, sender=Purchase)
def notify_approval(sender, instance, **kwargs):
    send_mail(...)
```

### Add API Authentication
```python
# In settings.py REST_FRAMEWORK
'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.TokenAuthentication',
]
```

### Add Background Tasks
```python
# Install celery
# Configure task queue in settings.py
# Use @shared_task decorator
```

---

**System designed for military asset accountability with complete audit trail and role-based access control.**
