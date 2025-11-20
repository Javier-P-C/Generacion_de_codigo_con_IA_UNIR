# Test runner script for Pharmacy Management System (PowerShell)
# This script runs all tests: backend unit, backend integration, frontend unit, and frontend E2E

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Pharmacy Management System - Test Runner" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

function Print-Success {
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green
}

function Print-Error {
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red
}

function Print-Info {
    param($message)
    Write-Host "➜ $message" -ForegroundColor Yellow
}

# Helper to call docker compose regardless of CLI variant
function Invoke-Compose {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]] $Args
    )
    # Prefer plugin-based 'docker compose'
    $usePlugin = $false
    try {
        docker compose version | Out-Null
        $usePlugin = $true
    } catch { $usePlugin = $false }

    if ($usePlugin) {
        docker compose @Args
        return
    }

    # Fallback to classic docker-compose
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        docker-compose @Args
        return
    }

    throw "Docker Compose not found. Install it or enable WSL integration in Docker Desktop."
}

# Ensure backend service is running and ready to accept commands
function Ensure-Services {
    Print-Info "Ensuring Docker services are up"
    $backendId = ""
    try {
        $backendId = (Invoke-Compose ps -q backend) 2>$null
    } catch { $backendId = "" }

    if (-not $backendId) {
        Print-Info "Starting services with compose up -d (this may build images on first run)"
        Invoke-Compose up -d --build
    }

    # Wait until we can exec into backend (container is running)
    $maxWait = [int]([Environment]::GetEnvironmentVariable('WAIT_SECONDS'))
    if ($maxWait -le 0) { $maxWait = 90 }
    $waited = 0
    while ($true) {
        try {
            Invoke-Compose exec -T backend python -V | Out-Null
            break
        } catch {
            if ($waited -ge $maxWait) {
                Print-Error "Backend service did not become ready within $($maxWait)s"
                Invoke-Compose ps | Out-Null
                throw
            }
            Start-Sleep -Seconds 3
            $waited += 3
            Print-Info "Waiting for backend to be ready... $($waited)s"
            # Re-check service exists; if not, try to start again
            try {
                $backendId = (Invoke-Compose ps -q backend) 2>$null
            } catch { $backendId = "" }
            if (-not $backendId) {
                Invoke-Compose up -d --build
            }
        }
    }
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Print-Error "Docker is not running. Please start Docker first."
    exit 1
}

# Backend Tests
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "1. Running Backend Unit Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Print-Info "Testing: Authentication, Employees, Products, Inventory, Sales"

Ensure-Services

try {
    Invoke-Compose exec -T backend python manage.py test authapp employees products inventory sales --verbosity=2
    Print-Success "Backend unit tests passed"
} catch {
    Print-Error "Backend unit tests failed"
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "2. Running Backend Integration Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Print-Info "Testing: End-to-end workflows"

try {
    Invoke-Compose exec -T backend python manage.py test integration_tests --verbosity=2
    Print-Success "Backend integration tests passed"
} catch {
    Print-Error "Backend integration tests failed"
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "3. Running Frontend Unit Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Print-Info "Testing: Components and Pages"

Push-Location frontend
try {
    npm test -- --run
    Print-Success "Frontend unit tests passed"
} catch {
    Print-Error "Frontend unit tests failed"
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "4. Running Frontend E2E Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Print-Info "Testing: Complete user journeys"
Print-Info "Note: This requires the application to be running"

Push-Location frontend
try {
    npm run e2e
    Print-Success "Frontend E2E tests passed"
} catch {
    Print-Error "Frontend E2E tests failed"
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✓ All Tests Passed Successfully!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Backend Unit Tests" -ForegroundColor Green
Write-Host "  ✓ Backend Integration Tests" -ForegroundColor Green
Write-Host "  ✓ Frontend Unit Tests" -ForegroundColor Green
Write-Host "  ✓ Frontend E2E Tests" -ForegroundColor Green
Write-Host ""
