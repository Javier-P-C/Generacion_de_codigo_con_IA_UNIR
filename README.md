# ACTIVIDAD: Generacion_de_codigo_con_IA
Este proyecto fue generado completamente con IA solo  estas primeras líneas en español del README fueron hechas por un humano. 

# Pharmacy Management System

A complete full-stack pharmacy management system built with Django REST Framework and React.

## 🏗️ Architecture

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: React 18 + Vite
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker + Docker Compose

## 📋 Features

### Backend Features
- ✅ Custom User Model with role-based permissions (Manager/Assistant)
- ✅ Product management with multiple presentation types
- ✅ Inventory tracking with automatic stock updates
- ✅ Sales processing with multiple items per transaction
- ✅ Automatic total calculation and inventory deduction
- ✅ Business rule enforcement (non-negative inventory, manager-only operations)
- ✅ Comprehensive unit tests
- ✅ PEP8 compliant with type hints

### Frontend Features
- ✅ JWT-based authentication with auto-refresh
- ✅ Role-based access control and protected routes
- ✅ Dashboard with quick links
- ✅ Inventory management (view and increase stock)
- ✅ Product CRUD (Manager only)
- ✅ Employee CRUD (Manager only)
- ✅ Multi-item sale registration
- ✅ Sales history with detailed views
- ✅ Clean, responsive UI

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Git

### 1. Clone the repository
```bash
git clone <repository-url>
cd Generacion_de_codigo_con_IA_UNIR
```

### 2. Create environment file
```bash
cp .env.example .env
```

Edit `.env` if you want to customize settings (optional for development).

### 3. Build and run with Docker Compose
```bash
docker-compose up --build
```

If you previously ran the stack and want a completely clean start (removing the database volume), run:
```bash
docker-compose down -v
docker-compose up --build
```

This will:
- Create and configure the PostgreSQL database
- Run Django migrations
- Create a default superuser (admin/admin123)
- Build and serve the React frontend
- Start all services

### 4. Access the application

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

**Default Credentials**:
- Username: `admin`
- Password: `admin123`
- Role: Manager

These credentials are created automatically by the `create_default_superuser` management command after migrations finish. If you change them, update the management command in `backend/employees/management/commands/create_default_superuser.py` and rebuild.

## 📚 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (returns access & refresh tokens) |
| POST | `/api/auth/refresh/` | Refresh access token |

### Employees (Manager only for write operations)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/employees/` | List all employees | All authenticated |
| POST | `/api/employees/` | Create employee | Manager only |
| GET | `/api/employees/{id}/` | Get employee details | All authenticated |
| PUT | `/api/employees/{id}/` | Update employee | Manager only |
| DELETE | `/api/employees/{id}/` | Delete employee | Manager only |

### Products (Manager only for write operations)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/products/` | List all products | All authenticated |
| POST | `/api/products/` | Create product | Manager only |
| GET | `/api/products/{id}/` | Get product details | All authenticated |
| PUT | `/api/products/{id}/` | Update product | Manager only |
| DELETE | `/api/products/{id}/` | Delete product | Manager only |

### Inventory
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/inventory/` | List inventory | All authenticated |
| POST | `/api/inventory/{id}/increase/` | Increase stock | Manager only |

### Sales
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/sales/` | List all sales | All authenticated |
| POST | `/api/sales/` | Create new sale | All authenticated |
| GET | `/api/sales/{id}/` | Get sale details | All authenticated |
| GET | `/api/sales/{id}/details/` | Get sale items | All authenticated |

## 🗄️ Database Schema

### Employee
- Extends Django's AbstractUser
- Fields: `id`, `username`, `email`, `name`, `role` (MANAGER/ASSISTANT)

### Product
- Fields: `id`, `name`, `presentation`, `substance`, `price`
- Presentations: tablets, capsules, syrups, suspensions, solutions, pills, injectables

### Inventory
- Fields: `id`, `product` (FK), `quantity`
- Constraint: quantity >= 0

### Sale
- Fields: `id`, `employee` (FK, PROTECT), `date`, `total`

### SaleDetail
- Fields: `id`, `sale` (FK), `product` (FK, PROTECT), `quantity`, `subtotal`

## 🔐 Business Rules

1. **Inventory Constraints**:
   - Inventory quantity cannot be negative
   - Stock is checked before processing sales
   - Only Managers can increase inventory

2. **Role-Based Access**:
   - Assistants can register sales but cannot modify products or employees
   - Managers have full access to all operations

3. **Sale Processing**:
   - Automatically calculates total from sale items
   - Creates SaleDetail records for each product
   - Decreases inventory quantities atomically
   - Uses database transactions to ensure data consistency

4. **Data Protection**:
   - Employees with associated sales cannot be deleted (PROTECT)
   - Products in sale details cannot be deleted (PROTECT)

## 🧪 Running Tests

Backend tests cover all critical business logic:

```bash
# Enter the backend container
docker-compose exec backend bash

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test employees
python manage.py test products
python manage.py test inventory
python manage.py test sales
```

## 🛠️ Development

### Backend Development

```bash
# Access backend container
docker-compose exec backend bash

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Access Django shell
python manage.py shell
```

### Frontend Development

```bash
# Access frontend container
docker-compose exec frontend sh

# Or run locally for hot reload:
cd frontend
npm install
npm run dev
```

## 📦 Project Structure

```
.
├── backend/
│   ├── config/              # Django project settings
│   ├── employees/           # Employee app (custom user model)
│   ├── products/            # Product management
│   ├── inventory/           # Inventory tracking
│   ├── sales/               # Sales processing
│   ├── authapp/             # JWT authentication
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── api/             # API client and endpoints
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── stores/          # Zustand state management
│   │   └── main.jsx         # App entry point
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   └── vite.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DJANGO_SECRET_KEY`: Django secret key (change in production)
- `DJANGO_DEBUG`: Debug mode (0 for production)
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `FRONTEND_ORIGIN`: Frontend URL for CORS
- `VITE_API_URL`: Backend API URL for frontend

## 🧪 Testing

This project includes comprehensive unit and integration tests for both backend and frontend.

### Backend Tests

#### Running All Backend Tests

```bash
# Inside Docker container
docker-compose exec backend python manage.py test

# Outside Docker (requires local Python environment)
cd backend
python manage.py test
```

#### Running Specific Test Modules

```bash
# Test authentication
docker-compose exec backend python manage.py test authapp

# Test employees
docker-compose exec backend python manage.py test employees

# Test products
docker-compose exec backend python manage.py test products

# Test inventory
docker-compose exec backend python manage.py test inventory

# Test sales
docker-compose exec backend python manage.py test sales

# Run integration tests
docker-compose exec backend python manage.py test integration_tests
```

#### Backend Test Coverage

**Authentication Tests** (`authapp/tests.py`):
- ✅ JWT token generation on login
- ✅ Token refresh functionality
- ✅ Manager access to restricted endpoints
- ✅ Assistant blocked from manager endpoints
- ✅ Unauthenticated access blocked

**Employee Tests** (`employees/tests.py`):
- ✅ Create employee (Manager only)
- ✅ Edit employee (Manager only)
- ✅ Delete employee (Manager only)
- ✅ List employees (all authenticated)
- ✅ Permission validation

**Product Tests** (`products/tests.py`):
- ✅ List products
- ✅ Create product with valid presentation
- ✅ Validate decimal price
- ✅ Edit product
- ✅ Delete product
- ✅ Invalid data validation

**Inventory Tests** (`inventory/tests.py`):
- ✅ List inventory
- ✅ Increase inventory (Manager only)
- ✅ Prevent negative inventory
- ✅ Validate non-negative quantities
- ✅ Auto-creation on product creation

**Sales Tests** (`sales/tests.py`):
- ✅ Create sale with multiple products
- ✅ Validate stock per item
- ✅ Calculate subtotals
- ✅ Calculate total price
- ✅ Verify inventory reduction
- ✅ Employees can list sales
- ✅ Employees can view sale details
- ✅ Insufficient stock handling

**Integration Tests** (`integration_tests.py`):
- ✅ Complete login flow with token storage
- ✅ Automatic token refresh
- ✅ Authenticated vs unauthenticated access
- ✅ Role-based route protection
- ✅ Complete CRUD workflows
- ✅ End-to-end sale process with inventory updates

### Frontend Tests

#### Running Frontend Unit Tests

```bash
# Inside frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

#### Frontend Unit Test Coverage

**Component Tests** (`src/__tests__/components.test.jsx`):
- ✅ Layout component renders without error
- ✅ Navigation links display correctly
- ✅ ProtectedRoute authentication check
- ✅ Role-based component visibility

**Page Tests** (`src/__tests__/pages.test.jsx`):
- ✅ Login page renders
- ✅ Form validation (empty fields)
- ✅ Error message display
- ✅ Dashboard, Products, Inventory, Sales pages render
- ✅ RegisterSale, Employees pages render

### Frontend E2E Tests (Playwright)

#### Running E2E Tests

```bash
# Inside frontend directory
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run e2e

# Run E2E tests with UI
npm run e2e:ui
```

#### E2E Test Coverage

**Authentication Flow** (`e2e/auth.spec.js`):
- ✅ Complete login with valid credentials
- ✅ Login with invalid credentials shows error
- ✅ Authenticated user can access application
- ✅ Unauthenticated user redirected to login
- ✅ Assistant blocked from manager routes
- ✅ Logout functionality

**Integration Workflows** (`e2e/integration.spec.js`):
- ✅ Create employee and verify in table
- ✅ Edit employee from UI
- ✅ Create product and verify in table
- ✅ Edit product from UI
- ✅ Delete product and verify removal
- ✅ Invalid product data shows errors
- ✅ Show complete inventory list
- ✅ Increase inventory as manager
- ✅ Register sale with multiple products
- ✅ Sale with insufficient stock shows error
- ✅ Sales list loaded correctly
- ✅ View sale detail
- ✅ All screens load after login
- ✅ Success messages on create/edit operations

### Test Statistics

| Test Type | Location | Count | Coverage |
|-----------|----------|-------|----------|
| **Backend Unit** | `backend/*/tests.py` | 80+ tests | Authentication, CRUD, Validations |
| **Backend Integration** | `backend/integration_tests.py` | 20+ tests | End-to-end workflows |
| **Frontend Unit** | `frontend/src/__tests__/` | 15+ tests | Components, Pages, Forms |
| **Frontend E2E** | `frontend/e2e/` | 20+ tests | Complete user journeys |
| **Total** | - | **135+ tests** | Full stack coverage |

### Running All Tests

#### Quick Test (All Tests at Once)

**Linux/Mac:**
```bash
chmod +x run-tests.sh
./run-tests.sh
```

**Windows (PowerShell):**
```powershell
.\run-tests.ps1
```

#### Manual Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend unit tests
cd frontend && npm test

# Frontend E2E tests (requires app running)
docker-compose up -d
cd frontend && npm run e2e
```

### Continuous Integration

For CI/CD pipelines, run tests in this order:

1. **Backend Tests**: `docker-compose run backend python manage.py test`
2. **Frontend Unit Tests**: `cd frontend && npm test -- --run`
3. **Build Frontend**: `cd frontend && npm run build`
4. **E2E Tests**: Requires running application

### Test Development Guidelines

- **Backend**: Add tests in respective app's `tests.py`
- **Frontend Unit**: Add to `src/__tests__/`
- **Frontend E2E**: Add to `e2e/` directory
- Always test both success and failure cases
- Test authentication and permissions
- Verify error messages and validation

## 📝 Code Quality

- **Backend**: PEP8 compliant, type hints, docstrings
- **Frontend**: Clean component structure, proper state management
- **Testing**: 135+ comprehensive unit and integration tests
- **Error Handling**: Proper validation and error messages
- **Coverage**: Critical business logic fully tested

## 🚢 Deployment Notes

For production deployment:

1. Set `DJANGO_DEBUG=0`
2. Change `DJANGO_SECRET_KEY` to a strong random value
3. Set `DJANGO_ALLOWED_HOSTS` to your domain
4. Use a managed PostgreSQL service
5. Configure proper CORS origins
6. Use environment-specific .env files
7. Set up proper SSL/TLS certificates
8. Consider using gunicorn/uwsgi for Django

## 📄 License

This project is created for educational purposes.

## 👥 Default Users

The system creates a default superuser on first run:
- **Username**: admin
- **Password**: admin123
- **Role**: Manager

You can create additional users through the Employees management screen (Manager only).
