import React from 'react';
import { Navigate } from 'react-router-dom';

export default function Login() {
  // 기존 AuthPage로 리다이렉트
  return <Navigate to="/auth" replace />;
}


