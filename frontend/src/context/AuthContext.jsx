import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, registerApi, getMeApi } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initAuth() {
      const storedToken = localStorage.getItem('agriguardian_token');
      if (storedToken) {
        try {
          const userData = await getMeApi();
          setUser(userData);
        } catch (e) {
          console.warn("Session expired or invalid:", e);
          localStorage.removeItem('agriguardian_token');
          localStorage.removeItem('agriguardian_user');
          setUser(null);
        }
      }
      setLoading(false);
    }
    initAuth();
  }, []);

  const login = async (email, password) => {
    const tokenData = await loginApi(email, password);
    localStorage.setItem('agriguardian_token', tokenData.access_token);
    
    // Fetch profile
    const userData = await getMeApi();
    setUser(userData);
    localStorage.setItem('agriguardian_user', JSON.stringify(userData));
    return userData;
  };

  const register = async (name, email, password) => {
    await registerApi(email, password);
    return login(email, password);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('agriguardian_token');
    localStorage.removeItem('agriguardian_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
