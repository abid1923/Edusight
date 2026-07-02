import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './store/AuthContext';

// Layouts
import AuthLayout from './layouts/AuthLayout';
import MainLayout from './layouts/MainLayout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Learning from './pages/Learning';
import Insight from './pages/Insight';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Redirect Root path to Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Authentication Routes (Unprotected, redirects to dashboard if logged in) */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Dashboard Routes (Protected, redirects to login if not authenticated) */}
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/insight" element={<Insight />} />
          <Route path="/settings" element={<Navigate to="/dashboard" replace />} />
        </Route>

        {/* Fallback Redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
