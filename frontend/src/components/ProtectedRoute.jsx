import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

const ProtectedRoute = ({ children, managerOnly = false }) => {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (managerOnly && user?.role !== 'MANAGER') {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
