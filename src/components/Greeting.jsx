/**
 * Greeting component - shows personalized greeting
 * Shows "환영합니다 {user.name}님!" when logged in
 * Falls back to email if name is not available
 */
import React from 'react';
import { useAuth } from '../auth/AuthProvider.tsx';

export default function Greeting() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div>
        환영합니다 사용자님!
      </div>
    );
  }

  return (
    <div>
      환영합니다 {user.name?.trim() || user.email}님!
    </div>
  );
}
