/**
 * Authentication context provider
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../lib/api';

// Types
interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthed: boolean;
  signup: (email: string, password: string, name: string) => Promise<{ success: boolean; data?: any; error?: string }>;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<{ success: boolean; user?: User; error?: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Computed authentication state
  const isAuthed = Boolean(user);

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // rememberMe 설정 확인
        const rememberMe = localStorage.getItem('rememberMe') === 'true';
        console.log('Auto-login check:', { rememberMe, localStorage: localStorage.getItem('rememberMe') });
        
        if (!rememberMe) {
          // 자동 로그인이 비활성화된 경우 세션 확인하지 않음
          console.log('Auto-login disabled, skipping session check');
          setUser(null);
          setLoading(false);
          return;
        }

        console.log('Auto-login enabled, checking session...');
        console.log('Current cookies:', document.cookie);
        
        // Check session by calling /auth/me (using Vite proxy)
        const response = await fetch('/auth/me', {
          credentials: 'include'
        });
        
        console.log('Session check response:', response.status, response.ok);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
          const userData = await response.json();
          console.log('Session valid, user data:', userData);
          setUser(userData);
        } else {
          console.log('Session invalid or expired');
          setUser(null);
        }
      } catch (error) {
        // Session invalid or not logged in
        console.log('Session check error:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const signup = async (email: string, password: string, name: string) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/auth/email/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, name })
      });
      const data = await response.json();
      if (response.ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error || 'Network error' };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const login = async (email: string, password: string, rememberMe: boolean = true) => {
    try {
      // rememberMe 상태를 로컬 스토리지에 저장
      localStorage.setItem('rememberMe', rememberMe.toString());
      
      // 로그인 요청 (using Vite proxy)
      const response = await fetch('/auth/email/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });
      
      console.log('Login response status:', response.status);
      console.log('Login response headers:', Object.fromEntries(response.headers.entries()));
      console.log('Cookies after login:', document.cookie);
      
      if (!response.ok) {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Login failed' };
      }

      // 백엔드에서 반환하는 실제 사용자 정보 사용
      const loginData = await response.json();
      if (loginData.user) {
        setUser(loginData.user);
        return { success: true, user: loginData.user };
      } else {
        // 백엔드에서 사용자 정보를 반환하지 않는 경우 임시 사용자 정보 사용
        const tempUser = {
          id: 1,
          name: email.split('@')[0],
          email: email
        };
        setUser(tempUser);
        return { success: true, user: tempUser };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const logout = async () => {
    try {
      // Clear session on server side
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      // Clear local state
      setUser(null);
      // Clear rememberMe setting
      localStorage.removeItem('rememberMe');
      // Redirect to main dashboard
      window.location.href = '/';
    } catch (error) {
      // Even if server logout fails, clear local state
      setUser(null);
      // Clear rememberMe setting
      localStorage.removeItem('rememberMe');
      // Still redirect to main dashboard
      window.location.href = '/';
    }
  };

  // Debug handle (non-production, temporary)
  if (typeof window !== 'undefined') {
    (window as any).__HATCH_DEBUG__ = {
      setUser: (userData: User) => {
        setUser(userData);
      },
      getState: () => ({ user, isAuthed }),
      clear: () => {
        setUser(null);
      }
    };
  }

  const value: AuthContextType = {
    user,
    loading,
    isAuthed,
    signup,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
