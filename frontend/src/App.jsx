import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LayoutWrapper from './components/layout/LayoutWrapper';
import Dashboard from './pages/Dashboard/Dashboard';
import Login from './pages/Auth/Login';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

import Recommendations from './pages/Recommendations';
import WeatherPage from './pages/Weather';
import MarketPage from './pages/Market';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <LayoutWrapper>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/recommendations" element={<Recommendations />} />
                  <Route path="/weather" element={<WeatherPage />} />
                  <Route path="/market" element={<MarketPage />} />
                  <Route path="/alerts" element={<div className="p-6 text-gray-600">Disaster alerts are not implemented in this MVP.</div>} />
                  <Route path="/schemes" element={<div className="p-6 text-gray-600">Government schemes are not implemented in this MVP.</div>} />
                  <Route path="/profile" element={<div className="p-6 text-gray-600">Profile management is not implemented in this MVP.</div>} />
                </Routes>
              </LayoutWrapper>
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
