# MAMS Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   React     │ ──────> │   Django    │ ──────> │  Database   │
│  Frontend   │ <────── │   Backend   │ <────── │ (SQLite/PG) │
│  (Vercel)   │         │   (Render)  │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
```

## Backend Architecture

### Django Project Structure

```
backend/
├── mams/                 # Main project directory
│   ├── settings.py      # Environment-based configuration
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI application
├── accounts/             # User and authentication app
│   ├── models.py        # User, Role models
│   ├── views.py         # User management views
│   ├── serializers.py   # User serializers
│   ├── permissions.py   # RBAC permission classes
│   └── middleware.py    # Role-based access middleware
├── assets/               # Asset management app
│   ├── models.py        # Base, AssetType, Asset, Purchase, Transfer, Assignment, Expenditure
│   ├── views.py         # Asset management views
│   ├── serializers.py   # Asset serializers
│   ├── services.py      # Business logic for calculations
│   └── signals.py       # Automatic audit logging
└── audit/                # Audit logging app
    ├── models.py         # AuditLog model
    └── views.py          # Audit log views
```

### Database Schema Design

#### Entity Relationship Diagram (Conceptual)

```
User ──┬──> Role
       │
       └──> Base (assigned_base, for Base Commanders)

Base ──┬──> Asset (inventory)
       ├──> Purchase
       ├──> Transfer (source_base)
       ├──> Transfer (destination_base)
       ├──> Assignment
       └──> Expenditure

AssetType ──┬──> Asset
            ├──> Purchase
            ├──> Transfer
            ├──> Assignment
            └──> Expenditure

User ──> AuditLog (created_by)
```

#### Key Design Decisions

1. **Asset Model**: Represents current inventory state. Automatically updated by Purchase, Transfer, and Expenditure models.

2. **Audit Logging**: Immutable logs created via Django signals. Cannot be modified or deleted.

3. **Role-Based Access**: Implemented at multiple levels:
   - Model-level (queryset filtering)
   - View-level (permission classes)
   - Middleware-level (request interception)

4. **Inventory Calculation**: Centralized in `AssetCalculationService` to ensure consistency.

## Frontend Architecture

### React Application Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── Layout.jsx    # Main layout with navigation
│   │   └── PrivateRoute.jsx
│   ├── contexts/         # React contexts
│   │   └── AuthContext.jsx
│   ├── pages/            # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Purchases.jsx
│   │   ├── Transfers.jsx
│   │   ├── Assignments.jsx
│   │   ├── Expenditures.jsx
│   │   └── Inventory.jsx
│   ├── services/         # API services
│   │   └── api.js        # Axios configuration
│   └── App.jsx           # Main app component
```

### Data Flow

1. **Authentication Flow:**
   ```
   User Login → JWT Token → localStorage → Axios Interceptor → API Requests
   ```

2. **Dashboard Data Flow:**
   ```
   Dashboard Component → API Call → Django View → Service Layer → 
   Database Query → Response → Dashboard Display
   ```

3. **Role-Based UI:**
   ```
   User Login → AuthContext → Role Check → Conditional Rendering
   ```

## Security Architecture

### Authentication & Authorization

1. **JWT Tokens:**
   - Access token: 1 hour lifetime
   - Refresh token: 7 days lifetime
   - Automatic refresh on 401 errors

2. **RBAC Implementation:**
   - Permission classes check user role
   - Queryset filtering based on role
   - Middleware for additional security

3. **Audit Trail:**
   - All mutations logged automatically
   - Immutable audit records
   - User, timestamp, and action tracking

### Data Protection

1. **Input Validation:**
   - Django model validators
   - DRF serializer validation
   - Frontend form validation

2. **SQL Injection Prevention:**
   - Django ORM (parameterized queries)
   - No raw SQL queries

3. **XSS Prevention:**
   - React automatic escaping
   - No `dangerouslySetInnerHTML`

## Deployment Architecture

### Backend (Render)

```
GitHub Repository
    ↓
Render Web Service
    ↓
Build Process (build.sh)
    ↓
Gunicorn Server
    ↓
PostgreSQL Database
```

### Frontend (Vercel)

```
GitHub Repository
    ↓
Vercel Build
    ↓
Static Files (dist/)
    ↓
CDN Distribution
```

## Environment Configuration

### Local Development

- **Database**: SQLite (no external dependency)
- **Backend**: Django development server
- **Frontend**: Vite development server
- **CORS**: Localhost origins allowed

### Production

- **Database**: PostgreSQL (managed by Render)
- **Backend**: Gunicorn + WSGI
- **Frontend**: Static files on Vercel CDN
- **CORS**: Specific production domains

## Business Logic

### Inventory Calculation

The system maintains inventory through automatic updates:

1. **Purchase**: `Asset.quantity += Purchase.quantity`
2. **Transfer Out**: `Source Asset.quantity -= Transfer.quantity`
3. **Transfer In**: `Destination Asset.quantity += Transfer.quantity`
4. **Expenditure**: `Asset.quantity -= Expenditure.quantity`

### Dashboard Metrics

Calculated using `AssetCalculationService`:

- **Opening Balance**: Inventory at start date (calculated from history)
- **Closing Balance**: Inventory at end date
- **Net Movement**: Purchases + Transfers In - Transfers Out
- **Assigned Assets**: Sum of active assignments
- **Expended Assets**: Sum of expenditures in date range

## Scalability Considerations

1. **Database Indexing:**
   - Audit logs indexed on timestamp, model_name, user
   - Assets indexed on base + asset_type (unique together)

2. **Query Optimization:**
   - Select_related for foreign keys
   - Prefetch_related for reverse relations
   - Pagination for large datasets

3. **Caching Opportunities:**
   - Dashboard data (can be cached with TTL)
   - Base and AssetType lists (rarely change)

4. **Future Scaling:**
   - Redis for caching
   - Celery for async tasks
   - Database read replicas
   - CDN for static assets

## Monitoring & Logging

1. **Audit Logs:**
   - All data changes logged
   - Immutable records
   - Searchable by model, user, date

2. **Error Handling:**
   - Django logging configuration
   - Frontend error boundaries
   - API error responses

3. **Performance Monitoring:**
   - Database query logging (DEBUG mode)
   - API response times
   - Frontend performance metrics

## API Design Principles

1. **RESTful:**
   - Resource-based URLs
   - HTTP methods (GET, POST, PUT, DELETE)
   - Status codes

2. **Consistent Response Format:**
   - Success: 200/201 with data
   - Error: 400/401/403/404 with error details

3. **Pagination:**
   - Page-based pagination
   - Configurable page size

4. **Filtering:**
   - Query parameters for filtering
   - Date range filtering
   - Base and asset type filtering


