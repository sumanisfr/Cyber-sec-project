import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from './api';
import { useAuth } from './AuthContext';

const EMPTY_PROFILE = {
  username: '',
  role: '',
  tenant_id: 'default',
  full_name: '',
  bio: '',
  avatar_url: '',
  social_links: {
    google: '',
    facebook: '',
    linkedin: '',
    github: '',
  },
};

const SOCIAL_SHORTCUTS = [
  { key: 'google', label: 'Google', href: 'https://accounts.google.com/' },
  { key: 'facebook', label: 'Facebook', href: 'https://www.facebook.com/' },
  { key: 'linkedin', label: 'LinkedIn', href: 'https://www.linkedin.com/' },
  { key: 'github', label: 'GitHub', href: 'https://github.com/' },
];

function Auth() {
  const navigate = useNavigate();
  const { token, setToken } = useAuth();
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [tenant, setTenant] = useState('default');
  const [fullName, setFullName] = useState('');
  const [message, setMessage] = useState('');
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [savingProfile, setSavingProfile] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setProfile(EMPTY_PROFILE);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const res = await axios.get('/api/auth/me');
      setProfile({
        ...EMPTY_PROFILE,
        ...res.data,
        social_links: { ...EMPTY_PROFILE.social_links, ...(res.data.social_links || {}) },
      });
      setTenant(res.data.tenant_id || 'default');
      setFullName(res.data.full_name || '');
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to fetch profile.');
    }
  };

  const register = async () => {
    setMessage('');
    try {
      const res = await axios.post('/api/auth/register', {
        username,
        password,
        tenant_id: tenant,
        full_name: fullName,
      });
      setMode('login');
      setMessage(`${res.data.message}. Login with your new account.`);
    } catch (err) {
      setMessage(err.response?.data?.error || 'Registration failed.');
    }
  };

  const login = async () => {
    setMessage('');
    try {
      const res = await axios.post('/api/auth/login', {
        username,
        password,
        tenant_id: tenant,
      });
      setToken(res.data.token);
      setMessage('Login successful. Redirecting...');
      setTimeout(() => navigate('/malware'), 700);
    } catch (err) {
      setMessage(err.response?.data?.error || 'Login failed. Register first or check your password.');
    }
  };

  const logout = () => {
    setToken(null);
    setProfile(EMPTY_PROFILE);
    setMessage('Logged out.');
  };

  const updateSocialLink = (key, value) => {
    setProfile((current) => ({
      ...current,
      social_links: {
        ...current.social_links,
        [key]: value,
      },
    }));
  };

  const handleAvatarChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setProfile((current) => ({
        ...current,
        avatar_url: reader.result,
      }));
    };
    reader.readAsDataURL(file);
  };

  const saveProfile = async () => {
    setSavingProfile(true);
    setMessage('');
    try {
      const res = await axios.put('/api/auth/profile', {
        full_name: profile.full_name,
        bio: profile.bio,
        avatar_url: profile.avatar_url,
        social_links: profile.social_links,
      });
      setProfile({
        ...EMPTY_PROFILE,
        ...res.data.profile,
        social_links: { ...EMPTY_PROFILE.social_links, ...(res.data.profile.social_links || {}) },
      });
      setMessage(res.data.message);
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to save profile.');
    } finally {
      setSavingProfile(false);
    }
  };

  const initials = (profile.full_name || profile.username || 'CS')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((item) => item[0]?.toUpperCase())
    .join('');

  return (
    <div className="auth-shell">
      <div className="auth-stage">
        <section className="auth-card">
          <div className="auth-toggle">
            <button
              className={`auth-toggle-button ${mode === 'register' ? 'active' : ''}`}
              onClick={() => setMode('register')}
            >
              Sign up
            </button>
            <button
              className={`auth-toggle-button ${mode === 'login' ? 'active' : ''}`}
              onClick={() => setMode('login')}
            >
              Login
            </button>
          </div>

          <div className="auth-card-body">
            <h2 className="auth-title">
              {mode === 'login' ? 'Log in to your existing profile' : 'Create your secure profile'}
            </h2>

            <a className="social-cta google" href="https://accounts.google.com/" target="_blank" rel="noreferrer">
              <span className="social-icon">G</span>
              <span>Continue with Google</span>
            </a>

            <div className="auth-divider">
              <span />
              <strong>OR</strong>
              <span />
            </div>

            {mode === 'register' && (
              <div className="mb-3">
                <label className="form-label">Full name</label>
                <input
                  className="form-control auth-input"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                />
              </div>
            )}

            <div className="mb-3">
              <label className="form-label">{mode === 'login' ? 'Username or Email' : 'Username or email'}</label>
              <input
                className="form-control auth-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username or Email"
              />
            </div>

            {mode === 'register' && (
              <div className="mb-3">
                <label className="form-label">Tenant ID</label>
                <input
                  className="form-control auth-input"
                  value={tenant}
                  onChange={(e) => setTenant(e.target.value)}
                  placeholder="default"
                />
              </div>
            )}

            <div className="mb-3">
              <label className="form-label">Password</label>
              <div className="password-shell">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control auth-input password-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((current) => !current)}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <button className="btn auth-submit" onClick={mode === 'login' ? login : register}>
              {mode === 'login' ? 'LOGIN' : 'CREATE ACCOUNT'}
            </button>

            {mode === 'login' && (
              <button type="button" className="auth-link-button" onClick={() => setMessage('Use Register if you have not created an account yet.')}>
                Forgot Password?
              </button>
            )}

            {message && <div className="alert alert-info mt-3">{message}</div>}

            <p className="auth-help">
              If something is not right, use Register first, then login with the same email and password.
            </p>
          </div>
        </section>

        <section className="profile-card">
          <h3>Profile</h3>
          {token ? (
            <>
              <div className="profile-header">
                <div className="profile-avatar">
                  {profile.avatar_url ? (
                    <img src={profile.avatar_url} alt="Profile" className="profile-avatar-image" />
                  ) : (
                    <span>{initials || 'CS'}</span>
                  )}
                </div>
                <div>
                  <strong className="profile-name">{profile.full_name || profile.username}</strong>
                  <p className="mb-1">{profile.username}</p>
                  <small>{profile.role} in tenant {profile.tenant_id}</small>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Profile photo</label>
                <input className="form-control auth-input" type="file" accept="image/*" onChange={handleAvatarChange} />
              </div>

              <div className="mb-3">
                <label className="form-label">Full name</label>
                <input
                  className="form-control auth-input"
                  value={profile.full_name}
                  onChange={(e) => setProfile((current) => ({ ...current, full_name: e.target.value }))}
                  placeholder="Display name"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Bio</label>
                <textarea
                  className="form-control auth-input"
                  rows={4}
                  value={profile.bio}
                  onChange={(e) => setProfile((current) => ({ ...current, bio: e.target.value }))}
                  placeholder="Write a short profile bio"
                />
              </div>

              <div className="profile-links">
                {SOCIAL_SHORTCUTS.map((item) => (
                  <div className="profile-link-row" key={item.key}>
                    <label className="form-label">{item.label}</label>
                    <input
                      className="form-control auth-input"
                      value={profile.social_links[item.key] || ''}
                      onChange={(e) => updateSocialLink(item.key, e.target.value)}
                      placeholder={`${item.label} profile URL`}
                    />
                    <a
                      className="btn btn-outline-light btn-sm"
                      href={profile.social_links[item.key] || item.href}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open
                    </a>
                  </div>
                ))}
              </div>

              <div className="d-flex flex-wrap gap-2 mt-4">
                <button className="btn auth-submit compact" onClick={saveProfile} disabled={savingProfile}>
                  {savingProfile ? 'Saving...' : 'Save Profile'}
                </button>
                <button className="btn btn-outline-light" onClick={fetchProfile}>
                  Refresh
                </button>
                <button className="btn btn-outline-light" onClick={logout}>
                  Logout
                </button>
              </div>
            </>
          ) : (
            <p className="text-muted">Register or login to view and edit your profile, photo, and social links.</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default Auth;
