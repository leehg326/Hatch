/**
 * Route guard component (optional, off by default)
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';

export default function Guard({ children }) {
  const { user, loading } = useAuth();

  // Check if protection is enabled via global flag
  const isProtectionEnabled = window.__HATCH_PROTECT__ === true;

  // If protection is not enabled, render children normally
  if (!isProtectionEnabled) {
    return children;
  }

  // If protection is enabled, check authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">인증 확인 중...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

/*
Example usage (DO NOT ENABLE NOW):

<Route path="/contracts/*" element={
  <Guard><ContractsRouter /></Guard>
} />

To enable protection later, set:
window.__HATCH_PROTECT__ = true;
*/
