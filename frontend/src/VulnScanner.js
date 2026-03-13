import React, { useEffect, useState } from 'react';
import axios from './api';
import { useAuth } from './AuthContext';

function VulnScanner() {
  const { token } = useAuth();
  const [url, setUrl] = useState('');
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (token) {
      fetchHistory();
    } else {
      setHistory([]);
    }
  }, [token]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get('/api/vuln/history');
      setHistory(res.data.history || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const scan = async () => {
    setError(null);
    setReport(null);

    if (!url) {
      setError('Enter a target URL to scan.');
      return;
    }
    if (!token) {
      setError('Login first to run and save vulnerability scans.');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('/api/vuln/scan', { url });
      setReport(res.data);
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.error || 'Scan failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">Attack Surface Review</span>
          <h1>Website Vulnerability Scanner</h1>
          <p>Check a target for weak security headers, exposed paths, open ports, and common web attack signals.</p>
        </div>
        <div className="hero-card compact">
          <strong>{token ? 'Authenticated scan mode' : 'Login required'}</strong>
          <span>{token ? 'Reports will be stored in your history.' : 'Use the Secure App page to unlock scans.'}</span>
        </div>
      </section>

      <section className="content-grid">
        <div className="glass-card">
          <h5 className="card-title">Scan Target</h5>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
            />
            <button className="btn btn-primary" onClick={scan} disabled={loading}>
              {loading ? 'Scanning...' : 'Scan'}
            </button>
          </div>
          {error && <div className="alert alert-danger mt-3">{error}</div>}
          {!token && <div className="alert alert-warning mt-3 mb-0">Sign in to run the backend scan and view saved reports.</div>}
        </div>

        <div className="glass-card">
          <h5 className="card-title">Scan History</h5>
          {history.length === 0 ? (
            <p className="text-muted">No scans yet.</p>
          ) : (
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    <th>URL</th>
                    <th>Scanned At</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((scanItem) => (
                    <tr key={scanItem.id}>
                      <td className="text-break">{scanItem.url}</td>
                      <td>{new Date(scanItem.scanned_at).toLocaleString()}</td>
                      <td>
                        <button
                          className="btn btn-outline-light btn-sm"
                          onClick={async () => {
                            try {
                              const res = await axios.get(`/api/vuln/report/${scanItem.id}`);
                              setReport(res.data.report);
                            } catch (err) {
                              setError('Failed to load report.');
                            }
                          }}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {report && (
        <div className="glass-card">
          <h4 className="card-title">Scan Results</h4>
          <div className="mb-3">
            <strong>Target:</strong> {report.target}
          </div>
          <div className="row mb-3">
            {Object.entries(report.counts || {}).map(([level, count]) => (
              <div key={level} className="col-md-3 col-sm-6 mb-2">
                <div className="mini-stat-card">
                  <h6 className="card-title mb-1">{level}</h6>
                  <p className="card-text display-6 mb-0">{count}</p>
                </div>
              </div>
            ))}
          </div>
          {report.details && report.details.length > 0 ? (
            <div>
              <h5>Vulnerabilities</h5>
              <div className="list-group">
                {report.details.map((vuln, idx) => (
                  <div key={`${vuln.name}-${idx}`} className="list-group-item scan-result-item">
                    <div className="d-flex justify-content-between">
                      <strong>{vuln.name}</strong>
                      <span
                        className={`badge bg-${
                          vuln.level === 'Critical'
                            ? 'danger'
                            : vuln.level === 'High'
                            ? 'warning'
                            : vuln.level === 'Medium'
                            ? 'info'
                            : 'secondary'
                        }`}
                      >
                        {vuln.level}
                      </span>
                    </div>
                    <p className="mb-1">{vuln.description}</p>
                    <small className="text-muted">Fix: {vuln.fix}</small>
                    {vuln.evidence && (
                      <div className="mt-1">
                        <small className="text-muted">Evidence: {vuln.evidence}</small>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p>No vulnerabilities found.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default VulnScanner;
