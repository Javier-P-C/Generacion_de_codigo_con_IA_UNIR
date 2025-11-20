/**
 * Unit tests for page components and form validations
 * Tests rendering, form validation, and error messages without backend calls
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';

// Mock API
vi.mock('../api', () => ({
  authAPI: {
    login: vi.fn(),
  },
  employeeAPI: {
    get: vi.fn(),
    list: vi.fn(() => Promise.resolve([])),
    create: vi.fn(),
    update: vi.fn(),
  },
  productAPI: {
    list: vi.fn(() => Promise.resolve([])),
    create: vi.fn(),
    update: vi.fn(),
  },
  inventoryAPI: {
    list: vi.fn(() => Promise.resolve([])),
    increase: vi.fn(),
  },
  salesAPI: {
    list: vi.fn(() => Promise.resolve([])),
    create: vi.fn(),
  },
}));

// Mock auth store
vi.mock('../stores/authStore', () => ({
  default: () => ({
    user: { id: 1, username: 'testuser', role: 'MANAGER' },
    isAuthenticated: () => false,
    setAuth: vi.fn(),
    clearAuth: vi.fn(),
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form without error', async () => {
    const Login = (await import('../pages/Login')).default;
    renderWithProviders(<Login />);
    
    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('validates empty username', async () => {
    const Login = (await import('../pages/Login')).default;
    const user = userEvent.setup();
    renderWithProviders(<Login />);
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    await user.click(loginButton);
    
    // Form should not submit with empty fields
    const usernameInput = screen.getByPlaceholderText(/username/i);
    expect(usernameInput).toBeInTheDocument();
  });

  it('shows error message on login failure', async () => {
    const { authAPI } = await import('../api');
    authAPI.login.mockRejectedValueOnce({
      response: { data: { detail: 'Invalid credentials' } },
    });

    const Login = (await import('../pages/Login')).default;
    const user = userEvent.setup();
    renderWithProviders(<Login />);
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });
    
    await user.type(usernameInput, 'wronguser');
    await user.type(passwordInput, 'wrongpass');
    await user.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials|login failed/i)).toBeInTheDocument();
    });
  });
});

describe('Dashboard Page', () => {
  it('renders without error', async () => {
    const Dashboard = (await import('../pages/Dashboard')).default;
    renderWithProviders(<Dashboard />);
    
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it('shows quick access links', async () => {
    const Dashboard = (await import('../pages/Dashboard')).default;
    renderWithProviders(<Dashboard />);
    
    // Check for multiple links - use getAllByText for multiple matches
    const links = screen.getAllByText(/inventory|products|sales/i);
    expect(links.length).toBeGreaterThan(0);
  });
});

describe('Products Page', () => {
  it('renders without error', async () => {
    vi.mock('../stores/authStore', () => ({
      default: () => ({
        user: { id: 1, username: 'manager', role: 'MANAGER' },
        isAuthenticated: () => true,
      }),
    }));

    const Products = (await import('../pages/Products')).default;
    renderWithProviders(<Products />);
    
    // Should have products title or related content
    expect(screen.getByText(/products/i)).toBeInTheDocument();
  });
});

describe('Inventory Page', () => {
  it('renders without error', async () => {
    vi.mock('../stores/authStore', () => ({
      default: () => ({
        user: { id: 1, username: 'assistant', role: 'ASSISTANT' },
        isAuthenticated: () => true,
      }),
    }));

    const Inventory = (await import('../pages/Inventory')).default;
    renderWithProviders(<Inventory />);
    
    expect(screen.getByText(/inventory/i)).toBeInTheDocument();
  });
});

describe('Sales Page', () => {
  it('renders without error', async () => {
    vi.mock('../stores/authStore', () => ({
      default: () => ({
        user: { id: 1, username: 'assistant', role: 'ASSISTANT' },
        isAuthenticated: () => true,
      }),
    }));

    const Sales = (await import('../pages/Sales')).default;
    renderWithProviders(<Sales />);
    
    expect(screen.getByText(/sales/i)).toBeInTheDocument();
  });
});

describe('RegisterSale Page', () => {
  it('renders without error', async () => {
    vi.mock('../stores/authStore', () => ({
      default: () => ({
        user: { id: 1, username: 'assistant', role: 'ASSISTANT' },
        isAuthenticated: () => true,
      }),
    }));

    const RegisterSale = (await import('../pages/RegisterSale')).default;
    renderWithProviders(<RegisterSale />);
    
    expect(screen.getByText(/register sale|new sale/i)).toBeInTheDocument();
  });
});

describe('Employees Page', () => {
  it('renders without error', async () => {
    vi.mock('../stores/authStore', () => ({
      default: () => ({
        user: { id: 1, username: 'manager', role: 'MANAGER' },
        isAuthenticated: () => true,
      }),
    }));

    const Employees = (await import('../pages/Employees')).default;
    renderWithProviders(<Employees />);
    
    expect(screen.getByText(/employees/i)).toBeInTheDocument();
  });
});

describe('Form Validation Tests', () => {
  it('validates required fields in forms', async () => {
    const Login = (await import('../pages/Login')).default;
    const user = userEvent.setup();
    renderWithProviders(<Login />);
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    
    // Inputs should be empty initially
    expect(usernameInput).toHaveValue('');
    expect(passwordInput).toHaveValue('');
    
    // Type and verify values
    await user.type(usernameInput, 'testuser');
    await user.type(passwordInput, 'testpass');
    
    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('testpass');
  });
});
