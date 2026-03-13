import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from './api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function Dashboard() {
  const [stats, setStats] = useState({
    total_scans: 0,
    malware_detected: 0,
    vulnerability_reports: 0,
    fraud_detected: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get('/api/stats/summary')
      .then((res) => {
        setStats(res.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const chartData = {
    labels: ['Total Scans', 'Malware Detections', 'Vuln Reports', 'Fraud Detections'],
    datasets: [
      {
        label: 'Events',
        data: [stats.total_scans, stats.malware_detected, stats.vulnerability_reports, stats.fraud_detected],
        backgroundColor: ['#0f766e', '#b91c1c', '#d97706', '#115e59'],
      },
    ],
  };

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">SOC Workspace</span>
          <h1>Security Dashboard</h1>
          <p>Run malware scans, inspect websites, and screen suspicious job offers from one clean command center.</p>
        </div>
        <div className="hero-card">
          <strong>Live overview</strong>
          <span>{loading ? 'Refreshing telemetry...' : 'Telemetry ready'}</span>
        </div>
      </section>

      <section className="stat-grid">
        <div className="metric-card">
          <span>Total Scans</span>
          <strong>{stats.total_scans}</strong>
        </div>
        <div className="metric-card">
          <span>Malware Hits</span>
          <strong>{stats.malware_detected}</strong>
        </div>
        <div className="metric-card">
          <span>Vulnerability Reports</span>
          <strong>{stats.vulnerability_reports}</strong>
        </div>
        <div className="metric-card">
          <span>Fraud Flags</span>
          <strong>{stats.fraud_detected}</strong>
        </div>
      </section>

      <section className="content-grid">
        <div className="glass-card">
          <h3>Trend Overview</h3>
          <Bar data={chartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
        <div className="glass-card">
          <h3>Included Workflows</h3>
          <div className="stack-list">
            <div className="stack-item">
              <strong>Malware Lab</strong>
              <p>Inspect suspicious files with hash checks, entropy analysis, and downloadable reports.</p>
            </div>
            <div className="stack-item">
              <strong>Website Scanner</strong>
              <p>Review headers, exposure paths, open ports, and common web attack indicators.</p>
            </div>
            <div className="stack-item">
              <strong>Job Scam Checker</strong>
              <p>Flag fake hiring patterns like payment requests, pressure tactics, and suspicious recruiter behavior.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
