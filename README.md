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

## 📝 Code Quality

- **Backend**: PEP8 compliant, type hints, docstrings
- **Frontend**: Clean component structure, proper state management
- **Testing**: Comprehensive unit tests for all critical logic
- **Error Handling**: Proper validation and error messages

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
