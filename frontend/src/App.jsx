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
import ProfilePage from './pages/Profile';
import AlertsPage from './pages/Alerts';
import AnalyticsPage from './pages/Analytics';
import FarmManagement from './pages/FarmManagement';
import DeviceStatus from './pages/DeviceStatus';
import IrrigationControl from './pages/IrrigationControl';
import NotImplementedPage from './pages/NotImplemented';

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
                  <Route path="/alerts" element={<AlertsPage />} />
                  <Route path="/schemes" element={<NotImplementedPage title="Government Schemes" />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/farm-management" element={<FarmManagement />} />
                  <Route path="/irrigation" element={<IrrigationControl />} />
                  <Route path="/device-status" element={<DeviceStatus />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="*" element={<NotImplementedPage title="Page Not Found" />} />
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
