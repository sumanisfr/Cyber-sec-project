import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import axios from './api';

import Dashboard from './Dashboard';
import MalwareLab from './MalwareLab';
import VulnScanner from './VulnScanner';
import JobScamChecker from './JobScamChecker';
import Auth from './Auth';
import Admin from './Admin';
import { AuthProvider, useAuth } from './AuthContext';

function Header({ theme, toggleTheme }) {
  const { token, setToken } = useAuth();

  return (
    <nav className="navbar navbar-expand-lg app-navbar">
      <div className="container-fluid app-container">
        <NavLink className="navbar-brand brand-mark" to="/">
          CyberShield Lab
        </NavLink>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
          <span className="navbar-toggler-icon" />
        </button>
        <div className="collapse navbar-collapse" id="mainNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <NavLink className="nav-link" to="/">
                Dashboard
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/malware">
                Malware Lab
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/vuln">
                Vuln Scanner
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/job-scam">
                Job Scam Check
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/auth">
                Secure App
              </NavLink>
            </li>
          </ul>

          <div className="d-flex align-items-center gap-2 nav-actions">
            <button className="btn btn-sm btn-outline-secondary" onClick={toggleTheme}>
              {theme === 'dark' ? 'Day View' : 'Night View'}
            </button>
            <span className={`status-badge ${token ? 'online' : 'offline'}`}>
              {token ? 'Authenticated' : 'Guest Mode'}
            </span>
            {token ? (
              <button className="btn btn-sm btn-outline-secondary" onClick={() => setToken(null)}>
                Logout
              </button>
            ) : (
              <NavLink className="btn btn-sm btn-outline-secondary" to="/auth">
                Login
              </NavLink>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    axios
      .get('/api/auth/csrf-token')
      .then((res) => {
        if (res.data?.csrf_token) {
          axios.defaults.headers.common['X-CSRFToken'] = res.data.csrf_token;
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((current) => (current === 'dark' ? 'light' : 'dark'));

  return (
    <Router>
      <Header theme={theme} toggleTheme={toggleTheme} />
      <div className="app-container py-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/malware" element={<MalwareLab />} />
          <Route path="/vuln" element={<VulnScanner />} />
          <Route path="/job-scam" element={<JobScamChecker />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </div>
    </Router>
  );
}

export default function AppWithProvider() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
