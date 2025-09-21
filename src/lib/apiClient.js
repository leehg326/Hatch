/**
 * API client with automatic token management and refresh
 */

// Use relative URLs with Vite proxy

/**
 * Fetch JSON with automatic authorization header and token refresh
 */
export async function fetchJson(url, options = {}) {
  const accessToken = localStorage.getItem('accessToken');
  
  // Add authorization header if token exists
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  
  const config = {
    ...options,
    headers,
  };
  
  try {
    const response = await fetch(url, config);
    
    // Handle 401 - try to refresh token once
    if (response.status === 401 && accessToken) {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        try {
          const refreshResponse = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
          
          if (refreshResponse.ok) {
            const refreshData = await refreshResponse.json();
            
            // Update tokens
            localStorage.setItem('accessToken', refreshData.access_token);
            localStorage.setItem('refreshToken', refreshData.refresh_token);
            
            // Retry original request with new token
            headers.Authorization = `Bearer ${refreshData.access_token}`;
            const retryResponse = await fetch(url, {
              ...config,
              headers,
            });
            
            return retryResponse;
          } else {
            // Refresh failed, logout user
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            window.location.href = '/login';
            throw new Error('Session expired');
          }
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('user');
          window.location.href = '/login';
          throw new Error('Session expired');
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
        throw new Error('No refresh token');
      }
    }
    
    return response;
  } catch (error) {
    throw error;
  }
}

/**
 * Helper function to get current access token
 */
export function getAccessToken() {
  return localStorage.getItem('accessToken');
}

/**
 * Helper function to set tokens
 */
export function setTokens(accessToken, refreshToken) {
  localStorage.setItem('accessToken', accessToken);
  localStorage.setItem('refreshToken', refreshToken);
}

/**
 * Helper function to clear tokens
 */
export function clearTokens() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
}
