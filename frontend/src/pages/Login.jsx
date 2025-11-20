import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authAPI, employeeAPI } from '../api';
import useAuthStore from '../stores/authStore';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: () => authAPI.login(username, password),
    onSuccess: async (data) => {
      // Store tokens immediately so subsequent requests include Authorization header
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // Decode token to get user info (simple JWT parsing)
      const payload = JSON.parse(atob(data.access.split('.')[1]));
      const userId = payload.user_id;

      // Fetch user details (now authenticated via interceptor)
      try {
        const userDetails = await employeeAPI.get(userId);
        setAuth(userDetails, data.access, data.refresh);
        navigate('/');
      } catch (err) {
        setError('Failed to fetch user details');
      }
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Login failed');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    loginMutation.mutate();
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#ecf0f1',
      }}
    >
      <div
        style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          width: '100%',
          maxWidth: '400px',
        }}
      >
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Login</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Username</label>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Password</label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
              }}
            />
          </div>
          {error && (
            <div
              style={{
                background: '#e74c3c',
                color: 'white',
                padding: '0.5rem',
                borderRadius: '4px',
                marginBottom: '1rem',
              }}
            >
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={loginMutation.isPending}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
          >
            {loginMutation.isPending ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem', color: '#7f8c8d' }}>
          Default: admin / admin123
        </p>
      </div>
    </div>
  );
};

export default Login;
