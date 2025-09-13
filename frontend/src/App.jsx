import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import IncidentList from './components/IncidentList';
import IncidentDetail from './components/IncidentDetail';
import Navigation from './components/Navigation';

// Services
import { authService } from './services/auth';

const queryClient = new QueryClient();

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = (token) => {
    authService.setToken(token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.removeToken();
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-900">
          <Toaster 
            position="top-right"
            toastOptions={{
              style: {
                background: '#374151',
                color: '#f3f4f6',
              },
            }}
          />
          
          {!isAuthenticated ? (
            <LoginForm onLogin={handleLogin} />
          ) : (
            <>
              <Navigation onLogout={handleLogout} />
              <main className="container mx-auto px-4 py-8">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/incidents" element={<IncidentList />} />
                  <Route path="/incidents/:id" element={<IncidentDetail />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </main>
            </>
          )}
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
