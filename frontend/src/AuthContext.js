import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from './api';

const AuthContext = createContext({
  token: null,
  setToken: () => {},
});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('jwt_token'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('jwt_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('jwt_token');
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  return <AuthContext.Provider value={{ token, setToken }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
