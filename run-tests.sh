#!/bin/bash
# Test runner script for Pharmacy Management System
# This script runs all tests: backend unit, backend integration, frontend unit, and frontend E2E

set -e  # Exit on error

echo "======================================"
echo "Pharmacy Management System - Test Runner"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Determine docker compose command (prefer 'docker compose', fallback to 'docker-compose')
compose() {
    # Prefer plugin-based 'docker compose'
    if docker compose version >/dev/null 2>&1; then
        docker compose "$@"
        return $?
    fi
    # Fallback to classic docker-compose
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
        return $?
    fi
    # Neither available
    print_error "Docker Compose not found. Install it or enable WSL integration in Docker Desktop."
    exit 1
}

# Ensure backend service is running (start stack if needed)
ensure_services() {
    print_info "Ensuring Docker services are up"
    # If backend not running, start stack
    if [ -z "$(compose ps -q backend 2>/dev/null)" ]; then
        print_info "Starting services with compose up -d (this may build images on first run)"
        compose up -d --build
    fi

    # Wait until we can exec into backend (container is running)
    MAX_WAIT=${WAIT_SECONDS:-90}
    waited=0
    until compose exec -T backend sh -c 'python -V >/dev/null 2>&1' 2>/dev/null; do
        if [ $waited -ge $MAX_WAIT ]; then
            print_error "Backend service didn't become ready within ${MAX_WAIT}s"
            compose ps
            exit 1
        fi
        sleep 3
        waited=$((waited+3))
        print_info "Waiting for backend to be ready... (${waited}s)"
        # Try to start again if container disappeared
        if [ -z "$(compose ps -q backend 2>/dev/null)" ]; then
            compose up -d --build
        fi
    done
}

# Backend Tests
echo "======================================"
echo "1. Running Backend Unit Tests"
echo "======================================"
print_info "Testing: Authentication, Employees, Products, Inventory, Sales"

# Make sure services are up before running tests
ensure_services

if compose exec -T backend python manage.py test authapp employees products inventory sales --verbosity=2; then
    print_success "Backend unit tests passed"
else
    print_error "Backend unit tests failed"
    exit 1
fi

echo ""
echo "======================================"
echo "2. Running Backend Integration Tests"
echo "======================================"
print_info "Testing: End-to-end workflows"

if compose exec -T backend python manage.py test integration_tests --verbosity=2; then
    print_success "Backend integration tests passed"
else
    print_error "Backend integration tests failed"
    exit 1
fi

echo ""
echo "======================================"
echo "3. Running Frontend Unit Tests"
echo "======================================"
print_info "Testing: Components and Pages"

cd frontend
if npm test -- --run; then
    print_success "Frontend unit tests passed"
    cd ..
else
    print_error "Frontend unit tests failed"
    cd ..
    exit 1
fi

echo ""
echo "======================================"
echo "4. Running Frontend E2E Tests"
echo "======================================"
print_info "Testing: Complete user journeys"
print_info "Note: This requires the application to be running"

cd frontend
if npm run e2e; then
    print_success "Frontend E2E tests passed"
    cd ..
else
    print_error "Frontend E2E tests failed"
    cd ..
    exit 1
fi

echo ""
echo "======================================"
echo "✓ All Tests Passed Successfully!"
echo "======================================"
echo ""
echo "Test Summary:"
echo "  ✓ Backend Unit Tests"
echo "  ✓ Backend Integration Tests"
echo "  ✓ Frontend Unit Tests"
echo "  ✓ Frontend E2E Tests"
echo ""
