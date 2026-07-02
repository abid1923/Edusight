import React, { createContext, useContext, useState, useEffect } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch current user details
  const fetchProfile = async (authToken) => {
    try {
      setLoading(true);
      const response = await client.get('/api/users/profile', {
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      });
      setUser(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Run on mount to check if token exists and fetch profile
  useEffect(() => {
    if (token) {
      fetchProfile(token);
    } else {
      setLoading(false);
    }

    // Listen for unauthorized events from axios interceptor
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('auth-unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth-unauthorized', handleUnauthorized);
    };
  }, [token]);

  // Login handler - sends application/x-www-form-urlencoded as FastAPI expects
  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await client.post('/api/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const accessToken = response.data.access_token;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
      
      // Axios interceptor will automatically catch this token for subsequent requests
      await fetchProfile(accessToken);
      return true;
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Username atau password salah';
      setError(errMsg);
      setLoading(false);
      throw new Error(errMsg);
    }
  };

  // Register handler - sends JSON RegisterRequest
  const register = async (username, email, password, fullName) => {
    try {
      setError(null);
      setLoading(true);

      await client.post('/api/auth/register', {
        username,
        email,
        password,
        full_name: fullName || null,
      });

      setLoading(false);
      // Automatically log in the user after successful registration
      return await login(username, password);
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Registrasi gagal. Coba lagi.';
      setError(errMsg);
      setLoading(false);
      throw new Error(errMsg);
    }
  };

  // Logout handler
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setError(null);
  };

  // Update profile handler (useful in Settings)
  const updateProfileState = (updatedUser) => {
    setUser(updatedUser);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout,
    updateProfileState,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
