# Quick Start Guide - Running Tests

## Prerequisites

1. **Docker Desktop** running
2. **Application running**: `docker-compose up`
3. **Node.js** installed (for frontend tests outside Docker)

---

## Option 1: Run All Tests (Recommended)

### Windows (PowerShell)
```powershell
# From project root
.\run-tests.ps1
```

### Linux/Mac
```bash
# From project root
chmod +x run-tests.sh
./run-tests.sh
```

This will run all 135+ tests automatically:
- ✅ Backend Unit Tests
- ✅ Backend Integration Tests
- ✅ Frontend Unit Tests
- ✅ Frontend E2E Tests

---

## Option 2: Run Tests Individually

### Backend Tests

#### 1. All Backend Tests
```bash
docker-compose exec backend python manage.py test
```

#### 2. Authentication Tests Only
```bash
docker-compose exec backend python manage.py test authapp
```

#### 3. Employees Tests Only
```bash
docker-compose exec backend python manage.py test employees
```

#### 4. Products Tests Only
```bash
docker-compose exec backend python manage.py test products
```

#### 5. Inventory Tests Only
```bash
docker-compose exec backend python manage.py test inventory
```

#### 6. Sales Tests Only
```bash
docker-compose exec backend python manage.py test sales
```

#### 7. Integration Tests Only
```bash
docker-compose exec backend python manage.py test integration_tests
```

#### 8. Specific Test
```bash
docker-compose exec backend python manage.py test employees.tests.EmployeeTests.test_create_employee_as_manager
```

---

### Frontend Tests

#### 1. Unit Tests (Components & Pages)

**First time setup:**
```bash
cd frontend
npm install
```

**Run tests:**
```bash
cd frontend
npm test
```

**Run with UI:**
```bash
cd frontend
npm run test:ui
```

**Run with coverage:**
```bash
cd frontend
npm run test:coverage
```

#### 2. E2E Tests (Playwright)

**First time setup:**
```bash
cd frontend
npm install
npx playwright install
```

**Make sure app is running:**
```bash
docker-compose up
```

**Run E2E tests:**
```bash
cd frontend
npm run e2e
```

**Run with UI:**
```bash
cd frontend
npm run e2e:ui
```

**Run specific test file:**
```bash
cd frontend
npx playwright test e2e/auth.spec.js
```

---

## Test Output Examples

### Backend Test Success
```
...................................................................
----------------------------------------------------------------------
Ran 67 tests in 12.345s

OK
```

### Frontend Test Success
```
 ✓ src/__tests__/components.test.jsx (5)
 ✓ src/__tests__/pages.test.jsx (11)

 Test Files  2 passed (2)
      Tests  16 passed (16)
```

### E2E Test Success
```
Running 20 tests using 1 worker

  ✓ e2e/auth.spec.js:8:3 › complete login flow (2s)
  ✓ e2e/integration.spec.js:15:3 › create employee (3s)

  20 passed (45s)
```

---

## Troubleshooting

### Backend Tests Fail

**Problem:** Database connection error
```bash
# Solution: Restart containers
docker-compose down
docker-compose up -d
docker-compose exec backend python manage.py test
```

**Problem:** Migrations not applied
```bash
# Solution: Run migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py test
```

### Frontend Unit Tests Fail

**Problem:** Dependencies not installed
```bash
# Solution: Install dependencies
cd frontend
npm install
npm test
```

**Problem:** Module not found
```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm test
```

### E2E Tests Fail

**Problem:** Application not running
```bash
# Solution: Start application
docker-compose up -d
# Wait 30 seconds for services to be ready
cd frontend
npm run e2e
```

**Problem:** Playwright browsers not installed
```bash
# Solution: Install browsers
cd frontend
npx playwright install
npm run e2e
```

**Problem:** Port already in use
```bash
# Solution: Stop other services using ports 5000/8000
docker-compose down
# Kill any processes using the ports
# Windows: netstat -ano | findstr "5000"
# Linux/Mac: lsof -ti:5000 | xargs kill
docker-compose up -d
```

---

## CI/CD Integration

For automated testing in CI/CD pipelines:

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services to be ready
sleep 30

# 3. Run backend tests
docker-compose exec -T backend python manage.py test

# 4. Run frontend unit tests
cd frontend && npm ci && npm test -- --run

# 5. Build frontend
npm run build

# 6. Run E2E tests (optional, requires built app)
npm run e2e

# 7. Cleanup
docker-compose down -v
```

---

## Test Statistics

After running all tests, you should see:

| Test Type | Expected Count | Time (approx) |
|-----------|---------------|---------------|
| Backend Unit | 80+ tests | ~15 seconds |
| Backend Integration | 20+ tests | ~10 seconds |
| Frontend Unit | 15+ tests | ~5 seconds |
| Frontend E2E | 20+ tests | ~45 seconds |
| **Total** | **135+ tests** | **~75 seconds** |

---

## Quick Commands Cheat Sheet

```bash
# Run all tests (automated script)
.\run-tests.ps1  # Windows
./run-tests.sh   # Linux/Mac

# Backend only
docker-compose exec backend python manage.py test

# Frontend unit only
cd frontend && npm test

# Frontend E2E only (app must be running)
cd frontend && npm run e2e

# Specific backend module
docker-compose exec backend python manage.py test products

# With verbose output
docker-compose exec backend python manage.py test --verbosity=2

# Stop on first failure
docker-compose exec backend python manage.py test --failfast

# Frontend with coverage
cd frontend && npm run test:coverage

# E2E with UI
cd frontend && npm run e2e:ui
```

---

## Next Steps

1. ✅ Run all tests to ensure everything works
2. ✅ Review test files in `backend/*/tests.py`
3. ✅ Review test files in `frontend/src/__tests__/`
4. ✅ Review E2E tests in `frontend/e2e/`
5. ✅ Read `TESTING.md` for detailed test documentation
6. ✅ Add your own tests following the existing patterns

---

## Support

If you encounter issues:
1. Check `TESTING.md` for detailed documentation
2. Ensure Docker is running
3. Ensure all dependencies are installed
4. Check application logs: `docker-compose logs`
5. Restart containers: `docker-compose restart`
