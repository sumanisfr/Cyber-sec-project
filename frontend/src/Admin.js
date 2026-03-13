import React, { useEffect, useState } from 'react';
import axios from './api';

function Admin() {
  const [users, setUsers] = useState([]);
  const [malwareScans, setMalwareScans] = useState([]);
  const [vulnScans, setVulnScans] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await axios.get('/api/auth/admin/users');
      setUsers(res.data.users || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const fetchMalwareScans = async () => {
    try {
      const res = await axios.get('/api/malware/history');
      setMalwareScans(res.data.history || []);
    } catch (err) {
      console.error('Failed to load malware scans', err);
    }
  };

  const fetchVulnScans = async () => {
    try {
      const res = await axios.get('/api/vuln/history');
      setVulnScans(res.data.history || []);
    } catch (err) {
      console.error('Failed to load vulnerability scans', err);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchMalwareScans();
    fetchVulnScans();
  }, []);

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">Oversight</span>
          <h1>Admin Panel</h1>
          <p>Review users and recent activity across the malware and vulnerability modules.</p>
        </div>
      </section>

      {error && <div className="alert alert-danger">{error}</div>}

      <section className="admin-grid">
        <div className="glass-card">
          <h5 className="card-title">Users ({users.length})</h5>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Tenant</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.username}</td>
                      <td>{user.role}</td>
                      <td>{user.tenant_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="glass-card">
          <h5 className="card-title">Malware Scans ({malwareScans.length})</h5>
          <div className="table-responsive">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Status</th>
                  <th>Scanned At</th>
                </tr>
              </thead>
              <tbody>
                {malwareScans.slice(0, 10).map((scan) => (
                  <tr key={scan.id}>
                    <td className="text-break">{scan.filename}</td>
                    <td>{scan.status}</td>
                    <td>{new Date(scan.scanned_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card">
          <h5 className="card-title">Vulnerability Scans ({vulnScans.length})</h5>
          <div className="table-responsive">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Scanned At</th>
                </tr>
              </thead>
              <tbody>
                {vulnScans.slice(0, 10).map((scan) => (
                  <tr key={scan.id}>
                    <td className="text-break">{scan.url}</td>
                    <td>{new Date(scan.scanned_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="glass-card">
        <h5 className="card-title">System Features</h5>
        <div className="stack-list">
          <div className="stack-item">
            <p>Scheduled scan jobs through APScheduler.</p>
          </div>
          <div className="stack-item">
            <p>Alert hooks for critical findings.</p>
          </div>
          <div className="stack-item">
            <p>Tenant-aware malware, website, and job-scam workflows.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;
