/**
 * Unit tests for React components
 * Tests rendering without backend calls and form validations
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock zustand store
vi.mock('../stores/authStore', () => ({
  default: () => ({
    user: { username: 'testuser', role: 'ASSISTANT' },
    isAuthenticated: () => true,
    clearAuth: vi.fn(),
  }),
}));

// Import components after mocking
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';

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

describe('Layout Component', () => {
  it('renders without error', () => {
    renderWithProviders(<Layout><div>Test Content</div></Layout>);
    expect(screen.getByText('Pharmacy Management')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    renderWithProviders(<Layout><div>Test Content</div></Layout>);
    expect(screen.getByText('Inventory')).toBeInTheDocument();
    expect(screen.getByText('Sales')).toBeInTheDocument();
    expect(screen.getByText('Register Sale')).toBeInTheDocument();
  });

  it('renders children content', () => {
    renderWithProviders(<Layout><div>Test Content</div></Layout>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('shows logout button for authenticated users', () => {
    renderWithProviders(<Layout><div>Test</div></Layout>);
    expect(screen.getByText(/logout/i)).toBeInTheDocument();
  });
});

describe('ProtectedRoute Component', () => {
  it('renders children when authenticated', () => {
    renderWithProviders(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
