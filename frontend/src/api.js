import axios from 'axios';

function resolveApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://127.0.0.1:5000';
  }

  const { protocol, hostname, port } = window.location;
  if (port === '5000') {
    return `${protocol}//${hostname}:5000`;
  }

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:5000`;
  }

  return window.location.origin;
}

export const API_BASE_URL = resolveApiBaseUrl();

axios.defaults.baseURL = API_BASE_URL;
axios.defaults.withCredentials = false;

export default axios;
