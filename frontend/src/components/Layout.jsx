import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

const Layout = ({ children }) => {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const isManager = user?.role === 'MANAGER';

  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <nav
        style={{
          background: '#2c3e50',
          color: 'white',
          padding: '1rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold', fontSize: '1.2rem' }}>
            Pharmacy Management
          </Link>
          <Link to="/inventory" style={{ color: 'white', textDecoration: 'none' }}>
            Inventory
          </Link>
          <Link to="/sales" style={{ color: 'white', textDecoration: 'none' }}>
            Sales
          </Link>
          <Link to="/register-sale" style={{ color: 'white', textDecoration: 'none' }}>
            Register Sale
          </Link>
          {isManager && (
            <>
              <Link to="/products" style={{ color: 'white', textDecoration: 'none' }}>
                Products
              </Link>
              <Link to="/employees" style={{ color: 'white', textDecoration: 'none' }}>
                Employees
              </Link>
            </>
          )}
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>
            {user?.name} ({user?.role})
          </span>
          <button
            onClick={handleLogout}
            style={{
              background: '#e74c3c',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
          >
            Logout
          </button>
        </div>
      </nav>
      <main style={{ padding: '2rem' }}>{children}</main>
    </div>
  );
};

export default Layout;
