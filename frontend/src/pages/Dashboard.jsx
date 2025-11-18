import React from 'react';
import useAuthStore from '../stores/authStore';

const Dashboard = () => {
  const { user } = useAuthStore();

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <p>
        Role: <strong>{user?.role}</strong>
      </p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Quick Links</h2>
        <ul style={{ fontSize: '1.1rem', lineHeight: '2' }}>
          <li>
            <a href="/inventory">View Inventory</a>
          </li>
          <li>
            <a href="/register-sale">Register New Sale</a>
          </li>
          <li>
            <a href="/sales">View Sales History</a>
          </li>
          {user?.role === 'MANAGER' && (
            <>
              <li>
                <a href="/products">Manage Products</a>
              </li>
              <li>
                <a href="/employees">Manage Employees</a>
              </li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
